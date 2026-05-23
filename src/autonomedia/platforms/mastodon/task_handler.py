import asyncio
import os
import re
from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.config import settings

# Configuration
BROWSER_DATA_DIR = os.path.join(settings.BASE_BROWSER_DATA_DIR, "mastodon")
MASTODON_URL = settings.MASTODON_URL

async def publish_mastodon(content: str, task_id: str = None):
    """
    Handles Mastodon publishing task using the BrowserProvider.
    """
    async with BrowserProvider(BROWSER_DATA_DIR, task_id=task_id) as context:
        page = context.pages[0] if context.pages else await context.new_page()
        
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
        
        # Submit
        post_btn = page.get_by_role("button", name=re.compile(r"^(Post|Publish)$", re.IGNORECASE))
        await post_btn.wait_for(state="visible")
        await post_btn.click()
        
        # Verify
        post_locator = page.get_by_text(content, exact=True)
        await post_locator.wait_for(state="visible", timeout=15000)
        
        return {"status": "success", "content": content}
