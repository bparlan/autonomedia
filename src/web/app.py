import asyncio
import json
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("web.app")

import os
import tempfile

from src.database.client import DatabaseClient

app = FastAPI()
templates = Jinja2Templates(directory="src/web/templates")


def fromjson(value):
    if isinstance(value, str):
        try:
            result = json.loads(value)
            if isinstance(result, dict):
                return result
            return {}
        except Exception:
            return {}
    return value if isinstance(value, dict) else {}


templates.env.filters["fromjson"] = fromjson


# Helper to fetch sidebar data
async def get_sidebar_data(conn):
    return await conn.fetch("SELECT * FROM platform_health ORDER BY platform_name ASC")


@app.get("/", response_class=HTMLResponse)
async def command_center(request: Request):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        prepared_items = await conn.fetch(
            "SELECT * FROM content WHERE status = 'prepared' ORDER BY id ASC"
        )
        failed_items = await conn.fetch(
            "SELECT * FROM content WHERE status = 'failed' ORDER BY id ASC"
        )
        ready_items = await conn.fetch(
            "SELECT * FROM content WHERE status = 'ready_to_post' ORDER BY id ASC"
        )
        health = await get_sidebar_data(conn)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "prepared_items": prepared_items,
            "failed_items": failed_items,
            "ready_items": ready_items,
            "platform_health": health,
        },
    )


@app.get("/content", response_class=HTMLResponse)
async def content_page(request: Request):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        items = await conn.fetch(
            "SELECT * FROM content WHERE status = 'idea' ORDER BY id DESC"
        )
        health = await get_sidebar_data(conn)
    return templates.TemplateResponse(
        request=request,
        name="content.html",
        context={"items": items, "platform_health": health},
    )


@app.get("/rewrites", response_class=HTMLResponse)
async def rewrites_page(request: Request):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        items = await conn.fetch(
            "SELECT * FROM content WHERE status IN ('approved', 'rewriting', 'prepared', 'failed', 'ready_to_post') ORDER BY id DESC"
        )
        health = await get_sidebar_data(conn)
    return templates.TemplateResponse(
        request=request,
        name="rewrites.html",
        context={"items": items, "platform_health": health},
    )


@app.get("/prepared-content/{id}")
async def get_prepared_content(id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow(
            "SELECT prepared_content FROM content WHERE id = $1", id
        )
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        try:
            content = item["prepared_content"]
            if content is None:
                return {}
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            raise HTTPException(
                status_code=500, detail="Invalid prepared_content JSON in database"
            )


@app.post("/add")
async def add_item(
    request: Request,
    topic: str = Form(...),
    type: str = Form(...),
    source_idea: str = Form(...),
    link_url: str = Form(...),
    hashtags: str = Form(""),
):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        # Atomic ID generation to prevent collisions
        new_id = await conn.fetchval("SELECT COALESCE(COUNT(*), 0) + 1 FROM content")
        new_id_str = f"{new_id:03d}"

        tag_list = [t.strip() for t in hashtags.split(",") if t.strip()]

        await conn.execute(
            """
            INSERT INTO content (id, topic, type, status, source_idea, link_url, hashtags, mentions, platforms)
            VALUES ($1, $2, $3, 'idea', $4, $5, $6::jsonb, '{}'::jsonb, '["all"]'::jsonb)
        """,
            new_id_str,
            topic,
            type,
            source_idea,
            link_url,
            json.dumps(tag_list),
        )

    return RedirectResponse(url="/content", status_code=303)


@app.get("/edit-content-row/{id}")
async def edit_content_row(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    return templates.TemplateResponse(
        request=request, name="partials/content_edit_form.html", context={"item": item}
    )


@app.get("/cancel-edit-content/{id}")
async def cancel_edit_content(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    return templates.TemplateResponse(
        request=request, name="partials/content_row.html", context={"item": item}
    )


@app.post("/save-content-row/{id}")
async def save_content_row(
    request: Request,
    id: str,
    topic: str = Form(...),
    type: str = Form(...),
    source_idea: str = Form(...),
    link_url: str = Form(...),
    hashtags: str = Form(""),
):
    form_data = await request.form()
    platforms = form_data.getlist("platforms")

    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        tag_list = [t.strip() for t in hashtags.split(",") if t.strip()]

        await conn.execute(
            """
            UPDATE content 
            SET topic=$1, type=$2, source_idea=$3, link_url=$4, hashtags=$5::jsonb, platforms=$6::jsonb
            WHERE id=$7
        """,
            topic,
            type,
            source_idea,
            link_url,
            json.dumps(tag_list),
            json.dumps(platforms),
            id,
        )

        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)

    return templates.TemplateResponse(
        request=request, name="partials/content_row.html", context={"item": item}
    )


@app.delete("/delete-item/{id}")
async def delete_item(id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE id = $1", id)
    return HTMLResponse(content="")


@app.post("/approve-idea/{id}")
async def approve_idea(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE content SET status = 'approved' WHERE id = $1", id)
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    return templates.TemplateResponse(
        request=request, name="partials/content_row.html", context={"item": item}
    )


from src.autonomedia.ai.planner import process_rewrites

# ... (other imports)


@app.get("/status-fragment/{id}")
async def status_fragment(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    return templates.TemplateResponse(
        request=request, name="partials/content_row.html", context={"item": item}
    )


@app.post("/batch-generate")
async def batch_generate(request: Request):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        # Move all 'approved' to 'rewriting'
        await conn.execute(
            "UPDATE content SET status = 'rewriting' WHERE status = 'approved'"
        )

    # Trigger background task
    asyncio.create_task(process_rewrites())

    return RedirectResponse(url="/rewrites", status_code=303)


@app.post("/reset-failure/{id}")
async def reset_failure(id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE content SET status = 'idea' WHERE id = $1", id)
    return HTMLResponse(content="")


@app.get("/review/{id}")
async def review_page(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
        health = await get_sidebar_data(conn)
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={"item": item, "platform_health": health},
    )


@app.post("/review/{id}/approve")
async def approve_review(request: Request, id: str):
    form_data = await request.form()
    action = form_data.get("action")

    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        if action == "regenerate":
            await conn.execute(
                "UPDATE content SET status = 'approved' WHERE id = $1", id
            )
            return RedirectResponse(url="/", status_code=303)

        elif action == "approve":
            # TC07: Check current status before processing (with lock for atomicity)
            current_status = await conn.fetchval(
                "SELECT status FROM content WHERE id = $1 FOR UPDATE", id
            )
            if current_status != "prepared":
                raise HTTPException(
                    status_code=409,
                    detail="Content is not in 'prepared' state for approval",
                )

            # Fetch full item to get metadata for priority check
            full_item = await conn.fetchrow(
                "SELECT prepared_content, metadata FROM content WHERE id = $1", id
            )
            item = await conn.fetchrow(
                "SELECT prepared_content FROM content WHERE id = $1", id
            )
            prepared_data = (
                json.loads(full_item["prepared_content"])
                if full_item and full_item["prepared_content"]
                else {}
            )
            verification_status = {}

            # TC05: Return error if no healthy platforms available
            # Check existing healthy platforms for logging
            healthy_platforms_rows = await conn.fetch(
                "SELECT platform_name FROM platform_health WHERE is_healthy = TRUE"
            )
            healthy_platforms = {row["platform_name"] for row in healthy_platforms_rows}

            if not healthy_platforms:
                raise HTTPException(
                    status_code=400, detail="No healthy platforms available"
                )

            # Update text content from form and build verification_status in single pass
            for key, value in form_data.items():
                if key.startswith("platform_"):
                    plat = key.replace("platform_", "")
                    if plat in healthy_platforms:
                        prepared_data[plat] = value
                        # TC04: Only healthy platforms can be verified
                        is_verified = form_data.get(f"verify_{plat}", "false") == "true"
                        if is_verified:
                            # Add verified_at and expires_at timestamps per M14S1 spec
                            now = datetime.now(UTC)
                            # Check priority metadata for TTL override (24 hours vs 12 hours)
                            metadata = json.loads(
                                full_item.get("metadata", "{}") or "{}"
                            )
                            ttl_hours = 24 if metadata.get("priority", False) else 12

                            verification_status[plat] = {
                                "verified": True,
                                "verified_at": now.isoformat(),
                                "expires_at": (
                                    now + timedelta(hours=ttl_hours)
                                ).isoformat(),
                            }
                        else:
                            verification_status[plat] = {
                                "verified": False,
                                "verified_at": None,
                                "expires_at": None,
                            }
                    else:
                        # Log exclusion of unhealthy platform per review findings
                        logger.info(
                            "Platform excluded from approval (unhealthy)",
                            extra={"platform": plat, "content_id": id},
                        )
                        if plat in prepared_data:
                            del prepared_data[plat]

            # Ensure all healthy platforms have verification status entry
            for plat in prepared_data.keys():
                if plat not in verification_status:
                    verification_status[plat] = {
                        "verified": False,
                        "verified_at": None,
                        "expires_at": None,
                    }

            await conn.execute(
                """
                UPDATE content 
                SET prepared_content = $1, 
                    verification_status = $2,
                    status = 'ready_to_post'
                WHERE id = $3
            """,
                json.dumps(prepared_data),
                json.dumps(verification_status),
                id,
            )
            return RedirectResponse(url="/rewrites", status_code=303)


@app.get("/registry", response_class=HTMLResponse)
async def registry_page(request: Request):
    with open("src/autonomedia/content/mention_registry.json") as f:
        registry = json.load(f)
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        health = await get_sidebar_data(conn)
    return templates.TemplateResponse(
        request=request,
        name="registry.html",
        context={"registry": registry, "platform_health": health},
    )


@app.get("/platforms", response_class=HTMLResponse)
async def platforms_page(request: Request):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        health = await get_sidebar_data(conn)
    return templates.TemplateResponse(
        request=request, name="platforms.html", context={"platform_health": health}
    )


# ... (existing imports)


@app.post("/registry/update")
async def update_registry(request: Request):
    form_data = await request.form()
    new_json = form_data.get("registry_data")

    # Atomic write to registry
    temp_fd, temp_path = tempfile.mkstemp(dir="src/autonomedia/content/")
    try:
        with os.fdopen(temp_fd, "w") as f:
            f.write(new_json)
        os.replace(temp_path, "src/autonomedia/content/mention_registry.json")
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e


@app.post("/remove-from-queue/{id}")
async def remove_from_queue(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        # Reset to 'prepared' (unverified)
        await conn.execute(
            "UPDATE content SET status = 'prepared', verification_status = '{}'::jsonb WHERE id = $1",
            id,
        )
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    return templates.TemplateResponse(
        request=request, name="partials/content_row.html", context={"item": item}
    )
