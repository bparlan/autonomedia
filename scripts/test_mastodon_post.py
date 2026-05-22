import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from playwright.async_api import async_playwright

# Configuration
MASTODON_URL = os.getenv("MASTODON_URL", "https://mastodon.social")
# Use the same profile path as test_mastodon_profile.py
BROWSER_DATA_DIR = os.getenv("BROWSER_DATA_DIR", "./runtime/browser_profiles/mastodon")

def log(level, message, **kwargs):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(entry))

async def run():
    task_id = f"test-post-{uuid.uuid4().hex[:8]}"
    post_content = "Hi Mum!"
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            log("info", "Navigating to home", task_id=task_id)
            await page.goto(MASTODON_URL)
            await page.wait_for_load_state("networkidle")
            
            # 1. Compose / Auth Check
            # Mastodon's compose editor is typically a textbox. 
            # We want to avoid containers and hit the actual editable element.
            # "What's on your mind?" is the standard placeholder.
            compose_textarea = page.get_by_placeholder("What's on your mind?")
            
            # If that fails, try to find a textbox inside the drawer
            if not await compose_textarea.count():
                 compose_textarea = page.locator(".compose-form__autosuggest-wrapper textarea, .compose-form__autosuggest-wrapper div[contenteditable='true']")
            
            # If still not found, pause for manual intervention
            if not await compose_textarea.count():
                log("warning", "Compose area not found. Pausing for manual login...")
                await asyncio.get_event_loop().run_in_executor(None, lambda: input("Browser is open. Please log in manually, then press ENTER in this terminal to continue..."))
                
                # Re-verify
                compose_textarea = page.get_by_placeholder("What's on your mind?")

            await compose_textarea.first.fill(post_content)
            log("info", "Content injected", content=post_content)
            
            # 2. Submit
            # Mastodon's publish button is often labeled "Publish". 
            # Note: The button might be inside a form.
            # Using a broader locator might be more robust if specific naming changes.
            publish_btn = page.get_by_role("button", name="Publish")
            
            # Action: Ensure it is enabled before clicking
            await publish_btn.wait_for(state="visible")
            await publish_btn.click()
            log("info", "Publish clicked")
            
            # 3. Verify
            # Wait for the post to appear in the timeline (simple approach: wait for text visibility)
            # Mastodon timelines update; checking for the specific post text is the most reliable check.
            log("info", "Waiting for verification")
            try:
                # We expect to see our post text on the page
                post_locator = page.get_by_text(post_content)
                await post_locator.wait_for(state="visible", timeout=15000)
                log("info", "Success: Post verified on timeline", task_id=task_id)
                await page.screenshot(path=f"artifacts/verified_{task_id}.png")
            except Exception as e:
                log("error", "Verification failed", error=str(e))
                await page.screenshot(path=f"artifacts/failed_verify_{task_id}.png")
                raise e

        except Exception as e:
            log("error", "Task failed", error=str(e))
            sys.exit(1)
        finally:
            await context.close()

if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    asyncio.run(run())
