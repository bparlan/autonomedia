import asyncio
import os
import re
import random
import json
import logging
from datetime import datetime, timezone
from autonomedia.browser.provider import BrowserProvider
from autonomedia.core.config import settings
from autonomedia.core.logger import log_post_event

# Configuration
BROWSER_DATA_DIR = os.path.join(settings.BASE_BROWSER_DATA_DIR, "mastodon")
MASTODON_URL = settings.MASTODON_URL

logger = logging.getLogger("mastodon_adapter")

def log_event(message, task_id, level="info", **kwargs):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "task_id": task_id,
        **kwargs
    }
    logger.info(json.dumps(entry))

async def publish_mastodon(content: str, task_id: str = None):
    """
    Handles Mastodon publishing task using the BrowserProvider.
    """
    try:
        log_event("Starting browser session", task_id)
        async with BrowserProvider(BROWSER_DATA_DIR, task_id=task_id) as context:
            page = context.pages[0] if context.pages else await context.new_page()
            
            log_event("Navigating to platform", task_id)
            await page.goto(MASTODON_URL)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(random.uniform(0.5, 2.5))  # Wait like a human
            
            # Session Health Check (Auth Expiry)
            # Mastodon typically shows a Log in link or form if logged out.
            login_indicators = await page.get_by_role("link", name=re.compile(r"Log in|Sign in", re.IGNORECASE)).count()
            if login_indicators > 0:
                log_event("Auth expired", task_id, level="error")
                raise Exception("Session Health Check Failed: Auth expired. User must re-authenticate the profile.")

            log_event("Session health verified", task_id)

            # Compose
            compose_textarea = page.get_by_placeholder("What's on your mind?")
            if not await compose_textarea.count():
                    compose_textarea = page.locator(".compose-form__autosuggest-wrapper textarea, .compose-form__autosuggest-wrapper div[contenteditable='true']")

            if await compose_textarea.count() == 0:
                log_event("Compose area not found", task_id, level="error")
                raise Exception("Compose area not found (session might be expired or UI changed)")

            log_event("Compose area found", task_id)
            await compose_textarea.first.fill(content)
            await asyncio.sleep(random.uniform(0.5, 2.5)) # Patient UI interaction
            
            # Submit
            post_btn = page.get_by_role("button", name=re.compile(r"^(Post|Publish)$", re.IGNORECASE))
            await post_btn.wait_for(state="visible")
            
            if await post_btn.is_disabled():
                log_event("Post button disabled", task_id, level="error")
                raise Exception("Post button is disabled (Content may violate platform rules or limits not caught by adapter)")
                
            log_event("Submitting post", task_id)
            await asyncio.sleep(random.uniform(0.5, 2.5))
            await post_btn.click()
            
            # Verify
            log_event("Verifying post", task_id)
            post_locator = page.get_by_text(content, exact=True)
            await post_locator.wait_for(state="visible", timeout=15000)
            
            log_event("Post successful", task_id)
            return {"status": "success", "content": content}

    except Exception as e:
        log_event(f"Task execution failed: {str(e)}", task_id, level="error")
        raise e
