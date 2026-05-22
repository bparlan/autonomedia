import asyncio
from playwright.async_api import async_playwright
import os
import json
from datetime import datetime, timezone
import re

# Configuration
BROWSER_DATA_DIR = os.getenv("BROWSER_DATA_DIR", "./runtime/browser_profiles/mastodon")
MASTODON_URL = os.getenv("MASTODON_URL", "https://mastodon.social")

async def publish_mastodon(content: str):
    """
    Handles Mastodon publishing task using persistent browser session.
    """
    async with async_playwright() as p:
        # Set headless=False for final visual verification as requested
        context = await p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False, 
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            await page.goto(MASTODON_URL)
            await page.wait_for_load_state("networkidle")
            
            # Login Check
            if await page.get_by_role("link", name="Log in").count() > 0:
                raise Exception("Session expired: Redirected to login.")

            # Compose
            compose_textarea = page.get_by_placeholder("What's on your mind?")
            if not await compose_textarea.count():
                 compose_textarea = page.locator(".compose-form__autosuggest-wrapper textarea, .compose-form__autosuggest-wrapper div[contenteditable='true']")

            if await compose_textarea.count() == 0:
                raise Exception("Compose area not found (session might be expired)")

            await compose_textarea.first.fill(content)
            await asyncio.sleep(1) # Patient UI interaction
            
            # Submit - Target "Post" button as per user instruction
            # We use a regex to be safe and catch "Post" (common in Deck) or "Publish" (common in standard)
            post_btn = page.get_by_role("button", name=re.compile(r"^(Post|Publish)$", re.IGNORECASE))
            await post_btn.wait_for(state="visible")
            await post_btn.click()
            
            # Verify
            post_locator = page.get_by_text(content, exact=True)
            await post_locator.wait_for(state="visible", timeout=15000)
            
            return {"status": "success", "content": content}
            
        except Exception as e:
            # Re-raise to be handled by worker
            raise e
        finally:
            await context.close()
