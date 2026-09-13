"""Simple scheduler for cooldown-aware posting."""
import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from src.autonomedia.core.database import get_ready_ideas, mark_posted, update_idea_status, set_verification
from src.autonomedia.ai.rewrites import rewrite_for_platform
from src.autonomedia.platforms.mastodon.task_handler import MastodonHandler as MastodonHandlerOriginal
from src.autonomedia.platforms.linkedin.task_handler import LinkedInHandler as LinkedInHandlerOriginal
from src.autonomedia.platforms.x.task_handler import XHandler as XHandlerOriginal

logger = logging.getLogger("autonomedia.scheduler")

# Handler registry
HANDLERS = {
    "mastodon": MastodonHandlerOriginal,
    "linkedin": LinkedInHandlerOriginal,
    "x": XHandlerOriginal,
}

async def generate_platform_rewrites(idea_id: str, base_content: str, platforms: List[str], reference_link: str | None = None) -> Dict[str, str]:
    """Generate platform-specific rewrites for an idea."""
    rewrites = {}
    for platform in platforms:
        rewritten = rewrite_for_platform(base_content, platform, reference_link)
        rewrites[platform] = rewritten
    return rewrites

async def process_ready_ideas():
    """Main processing loop for ready-to-post ideas."""
    while True:
        try:
            ideas = await get_ready_ideas()
            logger.info(f"Found {len(ideas)} ready ideas"")
            for idea in ideas:
                await process_idea(idea)
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.exception(f"Error in scheduler loop: {e}")
            await asyncio.sleep(60)

async def process_idea(idea: Dict[str, Any]):
    """Process a single idea for all platforms."""
    idea_id = idea["id"]
    platforms = json.loads(idea["platforms"]) if isinstance(idea["platforms"], str) else idea["platforms"]
    verifications = json.loads(idea.get("verification_status", "{}"))
    cooldown_hours = float(idea.get("cooldown_hours", 168))
    base_content = idea["base_content"]
    reference_link = idea.get("link_url")

    for platform in platforms:
        if not verifications.get(platform, {}).get("verified", False):
            continue
        # Check cooldown
        last_posted = None
        if "last_posted" in idea.get("metadata", {}) and platform in idea["metadata"]["last_posted"]:
            last_posted = datetime.fromisoformat(idea["metadata"]["last_posted"][platform])
        if last_posted and datetime.now(timezone.utc) - last_posted < timedelta(hours=cooldown_hours):
            logger.info(f"Idea {idea_id} on platform {platform} still in cooldown")
            continue
        # Generate rewrite
        rewritten = await generate_platform_rewrites(idea_id, base_content, [platform], reference_link)
        text = rewritten[platform]
        # Post via handler
        handler_class = HANDLERS.get(platform)
        if not handler_class:
            logger.error(f"No handler for platform {platform}")
            continue
        # Use profile directory from env
        import os
        browser_data_dir = os.getenv(f"{platform.upper()}_BROWSER_DATA_DIR", "runtime/profiles")
        handler = handler_class(browser_data_dir, task_id=idea_id, auth_token=os.getenv(f"{platform.upper()}_AUTH_TOKEN"))
        try:
            result = await handler.post(text, options={})
            url = result.get("url") if isinstance(result, dict) else None
            await mark_posted(idea_id, platform, url)
            logger.info(f"Posted idea {idea_id} to {platform}: {url or 'no url'}")
        except Exception as e:
            logger.exception(f"Failed to post idea {idea_id} to {platform}: {e}")
            await update_idea_status(idea_id, "failed", {platform: {"error": str(e)}})
        await asyncio.sleep(1)  # Small delay between platforms
