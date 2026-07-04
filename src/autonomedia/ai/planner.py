import json
import logging

from src.autonomedia.ai.rewriting.context import RewriteContext
from src.autonomedia.ai.rewriting.gemini import GeminiProvider
from src.autonomedia.content.transforms.entity_normalizer import EntityNormalizer
from src.database.client import DatabaseClient

logger = logging.getLogger("ai_planner")


async def process_rewrites():
    """
    Background worker that processes all items with status 'rewriting'.
    This is intended to be called when the batch generation is triggered.
    """
    logger.info("Starting batch AI rewrite process...")

    pool = await DatabaseClient.get_pool()
    # Using a context manager for the connection
    async with pool.acquire() as conn:
        items = await conn.fetch("SELECT * FROM content WHERE status = 'rewriting'")

        if not items:
            logger.info("No items in 'rewriting' status found.")
            return

        provider = GeminiProvider()
        entity_normalizer = EntityNormalizer()

        for item in items:
            try:
                # 1. Prepare context
                tags = json.loads(item["hashtags"]) if item["hashtags"] else []
                # Simple extraction of mentions (assuming default platform or first one)
                mentions_json = json.loads(item["mentions"]) if item["mentions"] else {}
                mentions = (
                    mentions_json.get("default", [])
                    if isinstance(mentions_json, dict)
                    else []
                )

                context = RewriteContext(
                    source_idea=item["source_idea"],
                    tags=tags,
                    mentions=mentions,
                    url=item.get("link_url"),
                )

                # 2. Generate
                platforms = (
                    json.loads(item["platforms"]) if item["platforms"] else ["mastodon"]
                )
                if isinstance(platforms, list) and "all" in platforms:
                    platforms = ["mastodon", "x"]

                prepared_data = {}
                # The prompt will be constructed inside the loop for each platform

                for platform in platforms:
                    context.platform = platform

                    prompt = (
                        "Write exactly ONE social media post based on this idea. "
                        "Return ONLY the post content. "
                        "Do not include any introductory phrases, explanations, or quotes. "
                        f"Format the post specifically for {platform}. "
                        "Keep it engaging and platform-appropriate."
                    )

                    try:
                        rewritten_text = await provider.rewrite(context, prompt)
                        rewritten_text = entity_normalizer.normalize_text(
                            rewritten_text, platform
                        )
                        # Clean up: Ensure it doesn't return unnecessary fluff
                        prepared_data[platform] = rewritten_text.strip()
                    except Exception as e:
                        logger.error(
                            f"Failed to generate for {platform} on item {item['id']}: {e}"
                        )
                        # Ensure we still have a key for the platform, even if it failed
                        prepared_data[platform] = f"[GENERATION FAILED: {str(e)}]"

                # 3. Update to 'prepared'
                await conn.execute(
                    """
                    UPDATE content 
                    SET status = 'prepared', prepared_content = $1
                    WHERE id = $2
                """,
                    json.dumps(prepared_data),
                    item["id"],
                )

                logger.info(f"Successfully processed item {item['id']}")

            except Exception as e:
                logger.error(f"Failed to process item {item['id']}: {e}")
                await conn.execute(
                    """
                    UPDATE content 
                    SET status = 'failed', error_log = $1
                    WHERE id = $2
                """,
                    str(e),
                    item["id"],
                )
