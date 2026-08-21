import json
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from src.database.client import DatabaseClient

TEMPLATES_DIR = Path(__file__).parent / "templates"

app = FastAPI()
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def tojson_filter(value: any, indent: int | None = None) -> str:
    """JSON serialization filter for Jinja2."""

    return json.dumps(value, indent=indent)

env.filters["tojson"] = tojson_filter

def _row_to_dict(row) -> dict:
    """Convert asyncpg row to dict for template rendering."""
    if row is None:
        return {}
    return dict(row)

# Add fromjson filter
def fromjson_filter(value: any) -> dict:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}

env.filters["fromjson"] = fromjson_filter


# Helper function to get platform health for all pages
async def get_platform_health():
    """Get platform health data for sidebar display."""
    try:
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT platform_name, is_healthy FROM platform_health ORDER BY platform_name"
            )
            return [{"platform_name": r["platform_name"], "status": "healthy" if r["is_healthy"] else "unhealthy"} for r in rows]
    except Exception:
        return []


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page - Command Center."""
    platform_health = await get_platform_health()
    template = env.get_template("dashboard.html")
    html = template.render(
        request=request,
        ready_items=[],
        prepared_items=[],
        failed_items=[],
        sidebar_data=[],
        platform_health=platform_health,
    )
    return HTMLResponse(content=html)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/content", response_class=HTMLResponse)
async def content_page(request: Request):
    """Content management page."""
    try:
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            items = await conn.fetch(
                "SELECT * FROM content ORDER BY created_at DESC"
            )
    except Exception:
        items = []

    platform_health = await get_platform_health()
    template = env.get_template("content.html")
    html = template.render(
        request=request,
        items=items or [],
        platform_health=platform_health,
    )
    return HTMLResponse(content=html)


@app.post("/add", response_class=RedirectResponse)
async def add_content(
    request: Request,
    topic: str = Form(...),
    type: str = Form(...),
    source_idea: str = Form(...),
    link_url: str | None = Form(None),
    hashtags: str | None = Form(""),
):
    """Add new content item to database."""
    # Validate topic
    if len(topic) < 3 or len(topic) > 100:
        raise HTTPException(status_code=400, detail="Topic must be 3-100 characters")
    
    # Validate type enum
    if type not in ["RefLink", "SelfPromotion", "Social"]:
        raise HTTPException(status_code=400, detail="Invalid type")
    
    # Validate source_idea
    if len(source_idea) < 5:
        raise HTTPException(status_code=400, detail="Source idea must be at least 5 characters")
    
    # Validate link_url if provided
    if link_url and not link_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Parse hashtags
    tags = [t.strip() for t in hashtags.split(",") if t.strip()]
    if len(tags) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 hashtags allowed")
    for tag in tags:
        if len(tag) > 50:
            raise HTTPException(status_code=400, detail="Each hashtag must be 50 characters or less")
    
    try:
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO content (id, topic, type, status, source_idea, link_url, hashtags) "
                "VALUES (gen_random_uuid()::text, $1, $2, $3, $4, $5, $6)",
                topic, type, "idea", source_idea, link_url, json.dumps(tags)
            )
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")
    
    return RedirectResponse(url="/content", status_code=303)


@app.get("/rewrites", response_class=HTMLResponse)
async def rewrites_page(request: Request):
    """Rewrites management page."""
    try:
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            items = await conn.fetch(
                "SELECT * FROM content WHERE status IN ('approved', 'rewriting', 'prepared', 'failed') "
                "ORDER BY created_at DESC"
            )
    except Exception:
        items = []

    platform_health = await get_platform_health()
    template = env.get_template("rewrites.html")
    html = template.render(
        request=request,
        items=items or [],
        platform_health=platform_health,
    )
    return HTMLResponse(content=html)


@app.get("/registry", response_class=HTMLResponse)
async def registry_page(request: Request):
    """Registry management page."""
    registry_path = Path(__file__).parent.parent / "autonomedia" / "content" / "mention_registry.json"
    
    if not registry_path.exists():
        raise HTTPException(status_code=404, detail="Registry file not found")
    
    try:
        with open(registry_path) as f:
            registry_data = json.load(f)
    except json.JSONDecodeError:
        registry_data = {}
    
    platform_health = await get_platform_health()
    template = env.get_template("registry.html")
    html = template.render(
        request=request,
        registry=registry_data,
        platform_health=platform_health,
    )
    return HTMLResponse(content=html)


@app.post("/registry/update", response_class=RedirectResponse)
async def update_registry(registry_data: str = Form(...)):
    """Update registry JSON file atomically."""
    # Validate JSON
    try:
        parsed_data = json.loads(registry_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    
    registry_path = Path(__file__).parent.parent / "autonomedia" / "content" / "mention_registry.json"
    
    try:
        # Atomic write using tempfile
        fd, temp_path = tempfile.mkstemp(dir=registry_path.parent, suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(parsed_data, f, indent=2)
            # Preserve permissions
            os.chmod(temp_path, 0o640)
            # Replace original file
            os.replace(temp_path, registry_path)
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(status_code=500, detail="Unable to write registry file (permission denied)")
    except PermissionError:
        raise HTTPException(status_code=500, detail="Unable to write registry file (permission denied)")
    
    return RedirectResponse(url="/registry", status_code=303)


@app.get("/platforms", response_class=HTMLResponse)
async def platforms_page(request: Request):
    """Platforms status page with detailed constraints and limits."""
    try:
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            platform_health = await conn.fetch(
                "SELECT platform_name, is_healthy FROM platform_health ORDER BY platform_name"
            )
            # Map is_healthy boolean to status string for template
            platform_health = [
                {"platform_name": r["platform_name"], "status": "healthy" if r["is_healthy"] else "unhealthy"}
                for r in platform_health
            ]
    except Exception:
        platform_health = []

    # Get supported platforms and their detailed constraints
    from autonomedia.ai.rewriting.gemini import GeminiProvider
    from autonomedia.core.platform import (
        get_platform_constraints,
        get_supported_platforms,
    )

    detailed_platforms = []
    supported_platforms = get_supported_platforms()

    for platform_name in supported_platforms:
        # Get health status
        health_item = next((h for h in platform_health if h["platform_name"] == platform_name), None)
        status = "healthy" if health_item and health_item["status"] == "healthy" else "unknown"
        auth_available = health_item and health_item["status"] == "healthy"

        # Get constraints from platform abstraction layer
        constraints = get_platform_constraints(platform_name)

        # Get character limits and tone from AI rewriting module
        platform_char_limit = None
        platform_tone = None
        if constraints:
            # Get the AI constraints (merged structure)
            from autonomedia.ai.rewriting.gemini import GeminiProvider
            gemini = GeminiProvider()
            platform_char_limit = gemini._get_platform_char_limit(platform_name)
            platform_tone = gemini._get_platform_tone(platform_name)

        # Get rate limit status
        from autonomedia.platforms.linkedin.task_handler import LinkedInHandler
        from autonomedia.platforms.mastodon.task_handler import MastodonHandler
        from autonomedia.platforms.x.task_handler import XHandler

        rate_limit = None
        try:
            # Create handlers to get rate limits
            if platform_name == "linkedin":
                handler = LinkedInHandler(browser_data_dir="")
            elif platform_name == "x":
                handler = XHandler(browser_data_dir="")
            elif platform_name == "mastodon":
                handler = MastodonHandler(browser_data_dir="")
            else:
                continue

            # Get rate limit status
            rate_limit = await handler.get_rate_limit_status()
        except Exception:
            rate_limit = {"note": "Rate limit info unavailable"}

        detailed_platforms.append({
            "name": platform_name,
            "status": status,
            "auth_available": auth_available,
            "char_limit": platform_char_limit,
            "tone": platform_tone,
            "rate_limit": rate_limit,
            "constraints": constraints or {},
        })

    template = env.get_template("platforms.html")
    html = template.render(
        request=request,
        platforms=detailed_platforms,
    )
    return HTMLResponse(content=html)



@app.get("/platform-status")
async def platform_status():
    """Platform status API endpoint returning detailed JSON including constraints."""
    try:
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            health_rows = await conn.fetch(
                "SELECT platform_name, is_healthy FROM platform_health ORDER BY platform_name"
            )
            platform_health_data = [
                {"name": r["platform_name"], "status": "healthy" if r["is_healthy"] else "unhealthy"}
                for r in health_rows
            ]

            # Fetch platform constraints from the abstraction layer
            all_constraints = {}
            supported_platforms = get_supported_platforms()
            for platform in supported_platforms:
                constraints = get_platform_constraints(platform)
                if constraints:
                    all_constraints[platform] = constraints

            # Combine health, constraints, and detailed platform information
            detailed_platform_data = []
            for health_item in platform_health_data:
                platform_name = health_item["name"]
                combined_data = health_item.copy()
                combined_data["constraints"] = all_constraints.get(platform_name, {})
                detailed_platform_data.append(combined_data)

            return detailed_platform_data
    except Exception as e:
        logger.error(f"Error fetching platform status: {e}")
        return []


@app.get("/edit-content-row/{item_id}", response_class=HTMLResponse)
async def edit_content_row(request: Request, item_id: str):
    """Edit form page for specific content item."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    template = env.get_template("partials/content_edit_form.html")
    html = template.render(
        request=request,
        item=item,
    )
    return HTMLResponse(content=html)


@app.post("/save-content-row/{item_id}", response_class=RedirectResponse)
async def save_content_row(
    request: Request,
    item_id: str,
    topic: str = Form(...),
    type: str = Form(...),
    source_idea: str = Form(...),
    link_url: str | None = Form(None),
    hashtags: str | None = Form(""),
):
    """Save edited content item."""
    # Validate topic
    if len(topic) < 3 or len(topic) > 100:
        raise HTTPException(status_code=400, detail="Topic must be 3-100 characters")
    
    # Validate type enum
    if type not in ["RefLink", "SelfPromotion", "Social"]:
        raise HTTPException(status_code=400, detail="Invalid type")
    
    # Validate source_idea
    if len(source_idea) < 5:
        raise HTTPException(status_code=400, detail="Source idea must be at least 5 characters")
    
    # Validate link_url if provided
    if link_url and not link_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Parse hashtags
    tags = [t.strip() for t in hashtags.split(",") if t.strip()]
    if len(tags) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 hashtags allowed")
    
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        await conn.execute(
            "UPDATE content SET topic = $1, type = $2, source_idea = $3, "
            "link_url = $4, hashtags = $5 WHERE id = $6",
            topic, type, source_idea, link_url, json.dumps(tags), item_id
        )
    
    return RedirectResponse(url="/content", status_code=303)


@app.get("/cancel-edit-content/{item_id}", response_class=HTMLResponse)
async def cancel_edit_content(request: Request, item_id: str):
    """Cancel edit and return to edit form with original values."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    template = env.get_template("partials/content_edit_form.html")
    html = template.render(
        request=request,
        item=item,
    )
    return HTMLResponse(content=html)


@app.get("/prepared-content/{item_id}", response_class=HTMLResponse)
async def prepared_content(request: Request, item_id: str):
    """Prepared content preview for specific item."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    try:
        prepared = json.loads(item["prepared_content"]) if item["prepared_content"] else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in prepared_content")
    
    template = env.get_template("partials/review_form.html")
    html = template.render(
        request=request,
        item=item,
        prepared=prepared,
    )
    return HTMLResponse(content=html)


@app.get("/status-fragment/{item_id}", response_class=HTMLResponse)
async def status_fragment(request: Request, item_id: str):
    """Status fragment HTML for specific content item - returns actual status badge."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Render just the status cell with actual item status
    # Use the same logic as content_row.html status display
    item = _row_to_dict(item)
    
    # Inline the status badge rendering (same logic from content_row.html)
    status = item.get("status", "")
    verification = {}
    try:
        verification = json.loads(item.get("verification_status", "{}")) if item.get("verification_status") else {}
    except:
        verification = {}
    
    prepared = {}
    try:
        prepared = json.loads(item.get("prepared_content", "{}")) if item.get("prepared_content") else {}
    except:
        prepared = {}
    
    # Build status badge based on actual status
    status_html = "<td class='p-4 align-top'>"
    
    if status == "idea":
        status_html += "<span class='bg-gray-800 text-gray-300 border border-gray-700 px-2 py-1 rounded text-xs font-bold uppercase'>Idea</span>"
    elif status == "approved":
        status_html += "<span class='bg-indigo-900 text-indigo-200 border border-indigo-800 px-2 py-1 rounded text-xs font-bold uppercase animate-pulse'>Generating</span>"
    elif status == "rewriting":
        status_html += "<span class='bg-purple-900 text-purple-200 border border-purple-800 px-2 py-1 rounded text-xs font-bold uppercase animate-pulse'>Rewriting...</span>"
    elif status == "prepared":
        status_html += "<span class='bg-yellow-900 text-yellow-200 border border-yellow-800 px-2 py-1 rounded text-xs font-bold uppercase'>Verification Needed</span>"
    elif status == "ready_to_post":
        # Show platform verification status
        if prepared and verification:
            badges = []
            for platform in prepared.keys():
                vstatus = verification.get(platform, {})
                if vstatus.get("verified") == True:
                    badges.append(f"<span class='bg-green-600 text-white border border-green-500 px-2 py-1 rounded text-xs font-bold uppercase mr-1'>{platform.title()}: Verified - In Queue</span>")
                elif vstatus.get("verified") == False:
                    badges.append(f"<span class='bg-gray-600 text-gray-200 border border-gray-500 px-2 py-1 rounded text-xs font-bold uppercase mr-1'>{platform.title()}: Unverified</span>")
                else:
                    badges.append(f"<span class='bg-yellow-600 text-yellow-100 border border-yellow-500 px-2 py-1 rounded text-xs font-bold uppercase mr-1'>{platform.title()}: Pending</span>")
            status_html += "".join(badges) if badges else "<span class='bg-green-600 text-white border border-green-500 px-2 py-1 rounded text-xs font-bold uppercase'>Verified - In Queue</span>"
        else:
            status_html += "<span class='bg-green-600 text-white border border-green-500 px-2 py-1 rounded text-xs font-bold uppercase'>Verified - In Queue</span>"
    elif status == "published":
        status_html += "<span class='bg-emerald-900 text-emerald-200 border border-emerald-800 px-2 py-1 rounded text-xs font-bold uppercase'>Published ✓</span>"
    elif status == "failed":
        status_html += "<span class='bg-red-900 text-red-200 border border-red-800 px-2 py-1 rounded text-xs font-bold uppercase'>Failed ✕</span>"
    
    status_html += "</td>"
    return HTMLResponse(content=status_html)


@app.get("/review/{item_id}", response_class=HTMLResponse)
async def review_page(request: Request, item_id: str):
    """Review page for specific content item."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if item["status"] != "prepared":
        raise HTTPException(status_code=400, detail="Content must be in 'prepared' status for review")
    
    try:
        prepared = json.loads(item["prepared_content"]) if item["prepared_content"] else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in prepared_content")
    
    platform_health = await get_platform_health()
    template = env.get_template("review.html")
    html = template.render(
        request=request,
        item=item,
        prepared=prepared,
        platform_health=platform_health,
    )
    return HTMLResponse(content=html)


@app.post("/review/{item_id}/approve", response_class=RedirectResponse)
async def approve_review(request: Request, item_id: str, **form_data):
    """Approve content for posting."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if item["status"] != "prepared":
            raise HTTPException(status_code=400, detail="Content must be in 'prepared' status")
        
        # Check for healthy platforms
        healthy_platforms = await conn.fetch(
            "SELECT platform_name FROM platform_health WHERE is_healthy = true"
        )
        if not healthy_platforms:
            raise HTTPException(status_code=400, detail="No healthy platforms available")
        
        # Build verification_status JSON
        verification = {}
        for key, value in form_data.items():
            if key.startswith("verify_"):
                platform = key.replace("verify_", "")
                verification[platform] = {
                    "verified": value == "true",
                    "verified_at": "2025-01-01T00:00:00Z",
                    "expires_at": "2025-12-31T23:59:59Z",
                }
        
        await conn.execute(
            "UPDATE content SET verification_status = $1, status = $2 WHERE id = $3",
            json.dumps(verification),
            "ready_to_post",
            item_id
        )
    
    return RedirectResponse(url="/content", status_code=303)


@app.post("/batch-generate", response_class=HTMLResponse)
async def batch_generate(request: Request):
    """Batch generate content for approved items - returns updated items for HTMX."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE content SET status = 'idea' WHERE status = 'approved'"
        )
        items = await conn.fetch(
            "SELECT * FROM content WHERE status IN ('approved', 'rewriting', 'prepared', 'failed') ORDER BY created_at DESC"
        )
    
    template = env.get_template("partials/content_row.html")
    html_parts = [template.render(request=request, item=_row_to_dict(item)) for item in items]
    return HTMLResponse(content="".join(html_parts))


@app.post("/approve-idea/{item_id}", response_class=HTMLResponse)
async def approve_idea(request: Request, item_id: str):
    """Approve idea for rewriting - returns HTML fragment for HTMX."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if item["status"] != "idea":
            raise HTTPException(status_code=400, detail="Content must be in 'idea' status")
        
        await conn.execute(
            "UPDATE content SET status = 'approved' WHERE id = $1", item_id
        )
        # Return updated item dict for template
        item = _row_to_dict(item)
    
    template = env.get_template("partials/content_row.html")
    return HTMLResponse(content=template.render(request=request, item=item))


@app.post("/reset-failure/{item_id}", response_class=HTMLResponse)
async def reset_failure(request: Request, item_id: str):
    """Reset failed content status - returns HTML fragment for HTMX."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if item["status"] not in ["failed", "rewriting"]:
            raise HTTPException(status_code=400, detail="Content must be in 'failed' or 'rewriting' status")
        
        await conn.execute(
            "UPDATE content SET status = 'approved' WHERE id = $1", item_id
        )
        item = _row_to_dict(item)
    
    template = env.get_template("partials/content_row.html")
    return HTMLResponse(content=template.render(request=request, item=item))


@app.post("/remove-from-queue/{item_id}", response_class=HTMLResponse)
async def remove_from_queue(request: Request, item_id: str):
    """Remove content from queue - returns HTML fragment for HTMX."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if item["status"] not in ["approved", "rewriting"]:
            raise HTTPException(status_code=400, detail="Content must be in 'approved' or 'rewriting' status")
        
        await conn.execute(
            "UPDATE content SET status = 'approved' WHERE id = $1", item_id
        )
        item = _row_to_dict(item)
    
    template = env.get_template("partials/content_row.html")
    return HTMLResponse(content=template.render(request=request, item=item))


@app.delete("/delete-item/{item_id}", response_class=RedirectResponse)
async def delete_item(item_id: str):
    """Delete content item from database."""
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Content not found")
        
        await conn.execute("DELETE FROM content WHERE id = $1", item_id)
    
    return RedirectResponse(url="/content", status_code=303)