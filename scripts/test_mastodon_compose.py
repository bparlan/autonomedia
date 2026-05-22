import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from playwright.async_api import async_playwright

# Configuration
MASTODON_URL = os.getenv("MASTODON_URL", "https://mastodon.social")
BROWSER_DATA_DIR = os.getenv("BROWSER_DATA_DIR", "./browser_data/mastodon")

def log(level, message, **kwargs):
    """Structured JSON logging policy."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(entry))

async def run():
    task_id = f"test-compose-{int(time.time())}"
    
    async with async_playwright() as p:
        # Launch persistent context to reuse existing sessions
        context = await p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        
        # In persistent context, the first page is created for us usually, or we can create it from the context
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            log("info", "Navigating to Mastodon", url=MASTODON_URL, task_id=task_id)
            await page.goto(MASTODON_URL)
            await page.wait_for_load_state("networkidle")
            
            # Diagnostic: Capture state
            log("info", "Page loaded", url=page.url, title=await page.title())
            await page.screenshot(path=f"artifacts/debug_{task_id}.png")
            
            # 1. Locate Compose Area
            # The compose textarea in Mastodon often has a label or specific role.
            # Let's try multiple selectors.
            compose_textarea = page.get_by_label("Post")
            
            # If that fails, try to find ANY textbox
            if not await compose_textarea.count():
                compose_textarea = page.get_by_role("textbox")
            
            # Ensure it is interactable
            try:
                await compose_textarea.first.wait_for(state="visible", timeout=10000)
                # If we found multiple, use the first one
                compose_textarea = compose_textarea.first
            except:
                # Fallback: Maybe it's hidden behind a "New Post" button
                new_post_btn = page.get_by_role("button", name="New post")
                if await new_post_btn.is_visible():
                    await new_post_btn.click()
                    await compose_textarea.first.wait_for(state="visible", timeout=5000)
                    compose_textarea = compose_textarea.first
                else:
                    # Final diagnostic
                    html_content = await page.content()
                    log("error", "Compose area not found. Dumping content snippet.", content_len=len(html_content))
                    raise Exception("Could not locate compose textarea or 'New post' button.")

            # 2. Inject Text
            log("info", "Injecting content", task_id=task_id)
            test_text = "Autonomedia test run: Deterministic interaction check."
            await compose_textarea.fill(test_text)
            
            # 3. Verification
            content = await compose_textarea.input_value()
            if content == test_text:
                log("info", "Success: Content injected correctly", task_id=task_id)
                await page.screenshot(path=f"artifacts/success_{task_id}.png")
            else:
                raise Exception(f"Injection mismatch. Expected '{test_text}', got '{content}'")

        except Exception as e:
            log("error", str(e), task_id=task_id)
            await page.screenshot(path=f"artifacts/error_{task_id}.png")
            sys.exit(1)
            
        finally:
            await context.close()

if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    asyncio.run(run())
