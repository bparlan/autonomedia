import pytest
import asyncio
from playwright.sync_api import sync_playwright
import json
from src.database.client import DatabaseClient

@pytest.mark.e2e
def test_dashboard_edit_content(db_pool):
    """
    Scenario: User edits content via Dashboard UI and verifies DB update.
    """
    # 1. Prepare initial data
    content_id = "test-e2e-1"
    asyncio_loop = asyncio.get_event_loop()
    
    async def setup():
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO content (id, topic, type, status, source_idea, platforms, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """, content_id, "E2E-Topic", "TestType", "idea", "Original Idea", json.dumps(["mastodon"]))
    
    asyncio_loop.run_until_complete(setup())
    
    # 2. Browser Action
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
    
        # Navigate to dashboard content page where 'idea' status items live
        page.goto("http://127.0.0.1:8000/content")
        
        # Navigate to dashboard content page
        page.goto("http://127.0.0.1:8000/content")
        
        # Click edit button
        row = page.locator("tr", has_text="E2E-Topic")
        row.hover()
        row.get_by_role("button", name="Edit").click()
        
        # Wait for form
        edit_form = page.locator('form[hx-post="/save-content-row/test-e2e-1"]')
        edit_form.wait_for(state="visible")
        
        # Interact with the form
        edit_form.locator('input[name="source_idea"]').fill("Updated Idea via E2E")
        
        # Click save and check network response
        with page.expect_response("/save-content-row/test-e2e-1") as response_info:
            edit_form.get_by_role("button", name="Save").click()
            
        resp = response_info.value
        print(f"Response status: {resp.status}")
        
        # Wait for the row to swap
        page.wait_for_selector("#row-test-e2e-1")
        
        browser.close()

    # 3. Verify side effect
    async def verify():
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT source_idea FROM content WHERE id = $1", content_id)
            assert row['source_idea'] == "Updated Idea via E2E"

    asyncio_loop.run_until_complete(verify())
