import asyncio
import json

import pytest
from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_dashboard_edit_content(db_pool):
    """
    Scenario: User edits content via Dashboard UI and verifies DB update.
    """
    # 1. Prepare initial data
    content_id = "test-e2e-1"
    asyncio_loop = asyncio.get_event_loop()
    
    async def setup():
        async with db_pool.acquire() as conn:
            # Clear existing data for clean state
            await conn.execute("DELETE FROM content WHERE id = $1", content_id)
            await conn.execute("""
                INSERT INTO content (
                    id,
                    topic,
                    type,
                    status,
                    source_idea,
                    platforms,
                    created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """, content_id, "E2E-Topic", "TestType", "idea", "Original Idea",
            json.dumps(["mastodon"])
            content_id,
            "E2E-Topic",
            "TestType",
            "idea",
            "Original Idea",
            json.dumps(["mastodon"])
        )
                INSERT INTO content (id, topic, type, status, source_idea, platforms, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """, content_id, "E2E-Topic", "TestType", "idea", "Original Idea", json.dumps(["mastodon"]))
    
    await setup()

    # 2. Browser Action
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to dashboard content page where 'idea' status items live
        await asyncio.sleep(0.5) # Short delay for form rendering
        
        # Click edit button
        row = page.locator("tr", has_text="E2E-Topic")
        await edit_form.locator('input[name="source_idea"]').fill("Updated Idea via E2E")
        await row.get_by_role("button", name="Edit").click()
        
        async with page.expect_response("/save-content-row/test-e2e-1") as response_info:
        edit_form = page.locator('form[hx-post="/save-content-row/test-e2e-1"]')
        await edit_form.wait_for(state="visible")
        await asyncio.sleep(0.5) # Small delay for form rendering
        
        # Interact with the form
        await edit_form.locator('input[name="source_idea"]').wait_for(state="visible")
        await edit_form.locator('input[name="source_idea"]').fill("Updated Idea via E2E")
        
        # Click save and check network response
        async with page.expect_response("/save-content-row/test-e2e-1") as response_info:
            await edit_form.get_by_role("button", name="Save").click()
            
        resp = response_info.value
            row = await conn.fetchrow("SELECT source_idea FROM content WHERE id = $1", content_id)
        
        
        # Wait for the row to swap
        await page.wait_for_selector("#row-test-e2e-1")
        
        await browser.close()

    # 3. Verify side effect
    async def verify():
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT source_idea FROM content WHERE id = $1", content_id)
            assert row['source_idea'] == "Updated Idea via E2E"

    await verify()