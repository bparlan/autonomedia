from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sys
import json
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.client import DatabaseClient

app = FastAPI()
templates = Jinja2Templates(directory="src/web/templates")

def fromjson(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except:
            return value
    return value

templates.env.filters["fromjson"] = fromjson

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        content = await conn.fetch("SELECT * FROM content ORDER BY id ASC")
    return templates.TemplateResponse(request=request, name="index.html", context={"content": content})

@app.post("/add")
async def add_item(
    topic: str = Form(...), 
    type: str = Form(...), 
    source_idea: str = Form(...), 
    link_url: str = Form(...),
    hashtags: str = Form(""),
    mentions: str = Form("")
):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        # Atomic ID generation to prevent collisions
        new_id = await conn.fetchval("SELECT COALESCE(MAX(id::int), 0) + 1 FROM content")
        new_id_str = f"{new_id:03d}"
        
        tag_list = [t.strip() for t in hashtags.split(",") if t.strip()]
        mention_list = {"default": [m.strip() for m in mentions.split(",") if m.strip()]}
        
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, source_idea, link_url, hashtags, mentions)
            VALUES ($1, $2, $3, 'idea', $4, $5, $6::jsonb, $7::jsonb)
        """, new_id_str, topic, type, source_idea, link_url, json.dumps(tag_list), json.dumps(mention_list))
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit-row/{id}")
async def edit_row(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    return templates.TemplateResponse(request=request, name="partials/edit_form.html", context={"item": item})

@app.get("/cancel-edit/{id}")
async def cancel_edit(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    return templates.TemplateResponse(request=request, name="partials/row.html", context={"item": item})

@app.post("/save-row/{id}")
async def save_row(
    request: Request, 
    id: str, 
    topic: str = Form(...), 
    type: str = Form(...), 
    source_idea: str = Form(...), 
    link_url: str = Form(...),
    hashtags: str = Form(""),
    mentions: str = Form("")
):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        tag_list = [t.strip() for t in hashtags.split(",") if t.strip()]
        mention_list = {"default": [m.strip() for m in mentions.split(",") if m.strip()]}
        
        await conn.execute("""
            UPDATE content 
            SET topic=$1, type=$2, source_idea=$3, link_url=$4, hashtags=$5::jsonb, mentions=$6::jsonb 
            WHERE id=$7
        """, topic, type, source_idea, link_url, json.dumps(tag_list), json.dumps(mention_list), id)
        
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    
    return templates.TemplateResponse(request=request, name="partials/row.html", context={"item": item})

@app.delete("/delete-item/{id}")
async def delete_item(id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE id = $1", id)
    return HTMLResponse(content="")

@app.post("/toggle-status/{id}")
async def toggle_status(request: Request, id: str):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        # Move from idea -> approved -> prepared
        # This is the entry point for the Assembly Line
        await conn.execute("""
            UPDATE content 
            SET status = CASE 
                WHEN status = 'idea' THEN 'approved'
                WHEN status = 'approved' THEN 'idea'
                ELSE status 
            END 
            WHERE id = $1
        """, id)
        item = await conn.fetchrow("SELECT * FROM content WHERE id = $1", id)
    
    return templates.TemplateResponse(request=request, name="partials/row.html", context={"item": item})
