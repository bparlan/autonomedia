import asyncio
import json

import structlog

from src.autonomedia.ai.moderation import ModerationAdapter
from src.autonomedia.ai.rewriting.context import RewriteContext
from src.autonomedia.ai.rewriting.gemini import GeminiProvider
from src.autonomedia.content.transforms.entity_normalizer import EntityNormalizer
from src.autonomedia.core.utils.verification import (
    is_platform_verified,
    parse_verification_status,
)
from src.database.client import DatabaseClient

# Structured JSON logging as per Autonomedia guidelines
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()


class PostingSecretary:
    def __init__(self):
        self.provider = GeminiProvider()
        self.normalizer = EntityNormalizer()
        self.interval = 30  # seconds

    async def run(self):
        logger.info("secretary_started", interval=self.interval)
        while True:
            await self.process_new_ideas()
            await self.process_verified_content()
            await asyncio.sleep(self.interval)

    async def process_verified_content(self):
        """Process ready_to_post items with verified status per platform.

        Uses verification_status JSONB column to determine which platforms
        are verified and should be posted.
        """
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            # Fetch ready_to_post items with verification status
            rows = await conn.fetch("""
                SELECT id, prepared_content, verification_status
                FROM content 
                WHERE status = 'ready_to_post'
            """)
            for row in rows:
                verification_status = parse_verification_status(
                    row.get("verification_status")
                )
                if not verification_status:
                    logger.info(
                        "Skipping item without verification_status",
                        content_id=row["id"],
                    )
                    continue

                prepared_content = row.get("prepared_content")
                if isinstance(prepared_content, str):
                    try:
                        prepared_content = json.loads(prepared_content)
                    except (json.JSONDecodeError, TypeError):
                        prepared_content = {}

                for platform, vstatus in verification_status.items():
                    if not isinstance(vstatus, dict):
                        continue
                    if not is_platform_verified(verification_status, platform):
                        continue

                    logger.info(
                        "processing_verified_content",
                        content_id=row["id"],
                        platform=platform,
                    )

                    content = prepared_content.get(platform, "")

                    try:
                        # Dispatch to platform handler (currently only Mastodon implemented)
                        if platform == "mastodon":
                            from src.autonomedia.platforms.mastodon.task_handler import (
                                publish_mastodon,
                            )

                            await publish_mastodon(content, row["id"])

                        # Update post history
                        await conn.execute(
                            """
                            INSERT INTO post_history (content_id, platform, status)
                            VALUES ($1, $2, 'published')
                            ON CONFLICT (content_id, platform)
                            DO UPDATE SET status = 'published'
                        """,
                            row["id"],
                            platform,
                        )

                        # Update content status to published
                        await conn.execute(
                            """
                            UPDATE content 
                            SET status = 'published' 
                            WHERE id = $1
                        """,
                            row["id"],
                        )

                        logger.info(
                            "posted_successfully",
                            content_id=row["id"],
                            platform=platform,
                        )

                    except Exception as e:
                        logger.error(
                            "posting_failed",
                            content_id=row["id"],
                            platform=platform,
                            error=str(e),
                        )
                        await conn.execute(
                            """
                            INSERT INTO post_history (content_id, platform, status, error_log)
                            VALUES ($1, $2, 'failed', $3)
                            ON CONFLICT (content_id, platform)
                            DO UPDATE SET status = 'failed', error_log = $3
                        """,
                            row["id"],
                            platform,
                            str(e),
                        )

    async def process_new_ideas(self):
        """Process approved content through AI rewriting.

        Generates platform-specific rewrites and sets status to 'prepared'.
        """
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            # 1. Zombie Killer: Cleanup stale 'rewriting' tasks
            # If an item is stuck in 'rewriting' for > 30 minutes, reset to 'failed'
            await conn.execute("""
                UPDATE content 
                SET status = 'failed', error_log = 'Orphaned task: stuck in rewriting state'
                WHERE status = 'rewriting' 
                AND created_at < NOW() - INTERVAL '30 minutes'
            """)

            # 2. Atomic fetch: 'idea' -> 'rewriting'
            rows = await conn.fetch("""
                UPDATE content 
                SET status = 'rewriting' 
                WHERE id IN (
                    SELECT id FROM content WHERE status = 'idea' 
                    ORDER BY created_at ASC 
                    FOR UPDATE SKIP LOCKED 
                    LIMIT 5
                ) 
                RETURNING *
            """)

            for row in rows:
                task_id = row["id"]
                logger.info("processing_content", task_id=task_id)

                try:
                    # Determine target platforms
                    platforms_raw = row.get("platforms")
                    platforms = (
                        json.loads(platforms_raw)
                        if platforms_raw and platforms_raw != "[]"
                        else ["mastodon"]
                    )

                    if platforms == ["all"]:
                        platforms = list(ModerationAdapter.PLATFORM_LIMITS.keys())

                    prepared_data = {}
                    for platform in platforms:
                        # Fetch platform limits
                        limit = ModerationAdapter.PLATFORM_LIMITS.get(platform, {}).get(
                            "max_chars", 500
                        )

                        prompt = (
                            f"Rewrite for {platform}. Provide EXACTLY one final post. "
                            f"Do not include multiple options or explanations. "
                            f"Must be under {limit} characters. "
                            "POLICY: Use registered entity tags for known companies/brands if available in your internal knowledge. "
                            "If you are unsure of an official tag, use plain text name only. Do not hallucinate tags."
                        )

                        # Construct Context
                        context = RewriteContext(
                            source_idea=row["source_idea"], platform=platform
                        )

                        rewritten = await self.provider.rewrite(
                            context=context, prompt=prompt
                        )

                        # Post-process with EntityNormalizer for deterministic compliance
                        rewritten = self.normalizer.normalize_text(rewritten, platform)

                        # Validate immediately
                        ModerationAdapter.validate(platform, rewritten)
                        prepared_data[platform] = rewritten

                    # Transition to 'prepared' (Awaiting user review)
                    payload = json.dumps(prepared_data)
                    await conn.execute(
                        """
                        UPDATE content 
                        SET status = 'prepared', 
                            prepared_content = $1,
                            error_log = NULL
                        WHERE id = $2
                    """,
                        payload,
                        task_id,
                    )

                    logger.info("content_prepared", task_id=task_id, status="success")

                except Exception as e:
                    logger.error(
                        "content_preparation_failed", task_id=task_id, error=str(e)
                    )
                    await conn.execute(
                        """
                        UPDATE content 
                        SET status = 'failed', 
                            error_log = $1 
                        WHERE id = $2
                    """,
                        str(e),
                        task_id,
                    )


if __name__ == "__main__":
    secretary = PostingSecretary()
    try:
        asyncio.run(secretary.run())
    except KeyboardInterrupt:
        logger.info("secretary_stopped")
