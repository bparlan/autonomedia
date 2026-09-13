"""Manual one-shot posting for a topic."""
import argparse
import json
import logging
import os
from pathlib import Path

from src.autonomedia.core.database import store_idea, get_idea, update_idea_status, set_verification
from src.autonomedia.ai.rewrites import rewrite_for_platform
from src.autonomedia.handlers.mastodon import MastodonHandler
from src.autonomedia.handlers.linkedin import LinkedInHandler
from src.autonomedia.handlers.x import XHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("autonomedia.manual")

async def approve_idea(idea_id: str, platform: str, verified: bool):
    """Approve an idea for a platform (set verification)."""
    from src.autonomedia.core.database import set_verification
    await set_verification(idea_id, platform, verified)
    logger.info(f"Set {platform} verification to {verified} for idea {idea_id}")

async def run_one_shot(idea_id: str, platforms: List[str]):
    """One-shot posting for the idea on each platform."""
    idea = await get_idea(idea_id)
    if not idea:
        logger.error(f"Idea {idea_id} not found")
        return
    base_content = idea["base_content"]
    reference_link = idea.get("link_url")
    # Generate rewrites
    rewrites = {}
    for platform in platforms:
        rewrites[platform] = rewrite_for_platform(base_content, platform, reference_link)
    # For each platform, post using its handler
    import os
    for platform in platforms:
        logger.info(f"Posting idea {idea_id} to {platform}")
        browser_data_dir = os.getenv(f"{platform.upper()}_BROWSER_DATA_DIR", "runtime/profiles")
        handler_class = {"mastodon": MastodonHandler, "linkedin": LinkedInHandler, "x": XHandler}"[platform]
        handler = handler_class(browser_data_dir, task_id=idea_id, auth_token=os.getenv(f"{platform.upper()}_AUTH_TOKEN"))
        try:
            result = await handler.post(rewrites[platform], options={})
            url = result.get("url") if isinstance(result, dict) else None
            logger.info(f"Success posting to {platform}: {url or 'no url'}")
            await update_idea_status(idea_id, "posted", None)
        except Exception as e:
            logger.exception(f"Failed posting to {platform}: {e}")
            await update_idea_status(idea_id, "failed", {platform: {"error": str(e)}})

def parse_args():
    parser = argparse.ArgumentParser(description="One-shot posting for an idea")
    parser.add_argument("--idea-id", required=True, help="Existing idea ID (use --create first)"")
    parser.add_argument("--platforms", nargs='+", default=["mastodon", "linkedin", "x"], help="Platforms to post to")
    parser.add_argument("--create", action="store_true", help="Create a new idea with the given topic and content")
    parser.add_argument("--topic", help="Topic for new idea")
    parser.add_argument("--content", help="Base content for new idea")
    parser.add_argument("--link", help="Optional reference link")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    import asyncio
    asyncio.run(main(args))

async def main(args):
    # Initialize DB (ensure tables exist)
    from src.autonomedia.core.database import init_db
    await init_db()
    idea_id = args.idea_id
    if args.create:
        if not args.topic or not args.content:
            logger.error("--topic and --content required with --create")
            return
        idea_id = await store_idea(args.topic, args.content, args.platforms)
        logger.info(f"Created idea {idea_id}")
    else:
        # Ensure idea exists
        idea = await get_idea(idea_id)
        if not idea:
            logger.error(f"Idea {idea_id} not found")
            return
    # Approve for all platforms (set verification)
    for platform in args.platforms:
        await approve_idea(idea_id, platform, True)
    # Run one-shot posting
    await run_one_shot(idea_id, args.platforms)
