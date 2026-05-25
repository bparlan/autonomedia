import pytest
import asyncio
from playwright.async_api import async_playwright

# Configuration
BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_m12_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 1. Verify Content Domain (Textarea & Mentions Removal)
        await page.goto(f"{BASE_URL}/content")
        # Check textarea exists
        assert await page.is_visible("textarea[name='source_idea']")
        # Check mentions input is absent
        assert await page.query_selector("input[name='mentions']") is None
        print("Verified: Content Domain UI")

        # 2. Verify Status Animation
        # We need an item in 'approved' status. Assuming '001' exists.
        await page.goto(f"{BASE_URL}/content")
        # Click Approve on a row if present
        approve_btn = page.locator("button:has-text('Approve to AI')").first
        if await approve_btn.count() > 0:
            await approve_btn.click()
            # Check for Generating label with animate-pulse
            status_label = page.locator(".animate-pulse:has-text('Generating')").first
            assert await status_label.is_visible()
            print("Verified: Status Animation")

        # 3. Verify Registry (No ISE)
        response = await page.goto(f"{BASE_URL}/registry")
        assert response.status == 200
        print("Verified: Registry Page accessible")

        # 4. Verify AI Rewrite Actions & Review Page
        # We need a prepared item
        await page.goto(f"{BASE_URL}/rewrites")
        # Ensure action buttons exist
        review_btn = page.locator("a:has-text('Review')").first
        if await review_btn.count() > 0:
            await review_btn.click()
            # Check Review Page Structure
            assert await page.is_visible("textarea[name='platform_mastodon']")
            assert await page.is_visible("input[name='verify_mastodon']")
            
            # Verify payload logic
            # Click "Send Verified to Queue"
            await page.click("button[value='approve']")
            await page.wait_for_url(f"{BASE_URL}/rewrites")
            print("Verified: Review Dashboard & Queueing")

        # 5. Verify Queue Removal
        ready_btn = page.locator("button:has-text('Remove from Queue')").first
        if await ready_btn.count() > 0:
            await ready_btn.click()
            # Check status reverted to Review Needed (prepared)
            assert await page.is_visible("text='Review Needed'")
            print("Verified: Queue Removal")

        await browser.close()
