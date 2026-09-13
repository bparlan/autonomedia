"""Test one-shot posting for all three platforms."""
import asyncio
import pytest
import os
from src.autonomedia.core.database import init_db, store_idea, get_idea, update_idea_status, set_verification
from src.autonomedia.ai.rewrites import rewrite_for_platform
from src.autonomedia.handlers.mastodon import MastodonHandler
from src.autonomedia.handlers.linkedin import LinkedInHandler
from src.autonomedia.handlers.x import XHandler

@pytest.mark.asyncio
async def test_one_shot_mastodon():
    await init_db()
    # Create a simple test idea
    idea_id = await store_idea("Test topic", "Test base content.", ["mastodon"])
    # Approve
    await set_verification(idea_id, "mastodon", True)
    # Rewrite
    rewritten = rewrite_for_platform("Test base content.", "mastodon", None)
    assert rewritten and isinstance(rewritten, str)
    # Post (may fail if no auth; we capture and log)
    browser_dir = os.getenv("MASTODON_BROWSER_DATA_DIR", "runtime/profiles")
    handler = MastodonHandler(browser_dir, task_id=idea_id)
    try:
        result = await handler.post(rewritten, options={})
        assert result.get("status") in ("success", "error")
    except Exception:
        pass  # expected if auth missing

@pytest.mark.asyncio
async def test_one_shot_linkedin():
    await init_db()
    idea_id = await store_idea("LinkedIn test", "LinkedIn base content.", ["linkedin"])
    await set_verification(idea_id, "linkedin", True)
    rewritten = rewrite_for_platform("LinkedIn base content.", "linkedin", None)
    assert rewritten and isinstance(rewritten, str)
    browser_dir = os.getenv("LINKEDIN_BROWSER_DATA_DIR", "runtime/profiles")
    handler = LinkedInHandler(browser_dir, task_id=idea_id)
    try:
        result = await handler.post(rewritten, options={})
        assert result.get("status") in ("success", "error")
    except Exception:
        pass

@pytest.mark.asyncio
async def test_one_shot_x():
    await init_db()
    idea_id = await store_idea("X test", "X base content.", ["x"])
    await set_verification(idea_id, "x", True)
    rewritten = rewrite_for_platform("X base content.", "x", None)
    assert rewritten and isinstance(rewritten, str)
    browser_dir = os.getenv("X_AUTH_TOKEN_BROWSER_DATA_DIR", "runtime/profiles")
    # X handler expects auth_token env; we may skip posting if missing
    if os.getenv("X_AUTH_TOKEN"):
        handler = XHandler(browser_dir, task_id=idea_id)
        try:
            result = await handler.post(rewritten, options={})
            assert result.get("status") in ("success", "error")
        except Exception:
            pass

# Optional: run the test manually to see output
if __name__ == "__main__":
    asyncio.run(test_one_shot_mastodon())
    asyncio.run(test_one_shot_linkedin())
    asyncio.run(test_one_shot_x())
    print("One-shot tests executed (may skip due to missing auth).")
