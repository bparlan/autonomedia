# src/autonomedia/core/posting_routine.py
"""
Daily Posting Routine with Randomized Intervals (M14S1)
"""

import asyncio
import json
import random
from datetime import UTC, datetime, timedelta

import structlog

from src.autonomedia.core.utils.verification import (
    get_verified_at_timestamp,
    is_platform_verified,
    parse_verification_status,
)
from src.autonomedia.platforms.mastodon.task_handler import publish_mastodon
from src.autonomedia.database.client import DatabaseClient

# Structured JSON logging
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()

# Default TTL for verified content (12 hours)
DEFAULT_TTL_HOURS = 12
# Priority TTL override (24 hours)
PRIORITY_TTL_HOURS = 24
# Randomized delay range in minutes
MIN_DELAY_MINUTES = 2
MAX_DELAY_MINUTES = 10
# Minimum hours between posts for second item
SECOND_POST_MIN_HOURS = 8


def log_event(message: str, level: str = "info", **kwargs):
    """Helper for structured logging."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": level,
        "message": message,
        **kwargs,
    }
    logger.info(json.dumps(entry))


async def _apply_randomized_delay(
    min_minutes: int = MIN_DELAY_MINUTES, max_minutes: int = MAX_DELAY_MINUTES
):
    """Apply random delay between min_minutes and max_minutes before posting."""
    delay_seconds = random.randint(min_minutes * 60, max_minutes * 60)
    log_event(
        "Applying randomized delay",
        delay_seconds=delay_seconds,
        min_minutes=min_minutes,
        max_minutes=max_minutes,
    )
    await asyncio.sleep(delay_seconds)


async def _get_verified_content(platform: str) -> list:
    """
    Query ready_to_post items with verified status for the specified platform.
    Prioritizes by verified_at (recent first) and handles expiration.

    Args:
        platform: Platform name (e.g., 'mastodon')

    Returns:
        List of content rows that are verified and ready to post
    """
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT *
            FROM content
            WHERE status = 'ready_to_post'
            AND (verification_status -> $1 ->> 'verified')::boolean IS TRUE
            ORDER BY (verification_status -> $1 ->> 'verified_at') DESC NULLS LAST
        """,
            platform,
        )

        verified_items = []
        now = datetime.now(UTC)

        for row in rows:
            verification_status = parse_verification_status(
                row.get("verification_status")
            )
            if not is_platform_verified(verification_status, platform):
                log_event(
                    "Skipping non-verified item", level="warning", content_id=row["id"]
                )
                continue

            # Get platform-specific data for expiration check
            platform_data = verification_status.get(platform, {})
            if isinstance(platform_data, str):
                try:
                    platform_data = json.loads(platform_data)
                except (json.JSONDecodeError, TypeError):
                    platform_data = {}

            expires_at_str = (
                platform_data.get("expires_at")
                if isinstance(platform_data, dict)
                else None
            )

            # Check expiration
            should_skip = False
            if expires_at_str:
                try:
                    # Handle both 'Z' suffix and timezone-aware formats
                    if isinstance(expires_at_str, str):
                        if expires_at_str.endswith("Z"):
                            expires_at = datetime.fromisoformat(
                                expires_at_str.replace("Z", "+00:00")
                            )
                        else:
                            expires_at = datetime.fromisoformat(expires_at_str)
                    else:
                        expires_at = expires_at_str

                    metadata = row.get("metadata", {}) or {}
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except (json.JSONDecodeError, TypeError):
                            metadata = {}
                    is_priority = metadata.get("priority", False)

                    if now > expires_at and not is_priority:
                        log_event(
                            "Skipping expired item",
                            level="warning",
                            content_id=row["id"],
                        )
                        should_skip = True
                except (ValueError, TypeError, AttributeError) as e:
                    log_event(
                        "Malformed expires_at, skipping",
                        level="warning",
                        content_id=row["id"],
                        error=str(e),
                    )
                    should_skip = True

            if not should_skip:
                verified_items.append(row)

        # Sort by verified_at descending (most recent first)
        verified_items.sort(
            key=lambda item: get_verified_at_timestamp(
                parse_verification_status(item.get("verification_status")), platform
            ),
            reverse=True,
        )

        return verified_items


async def _get_last_posted_at(platform: str) -> datetime | None:
    """
    Get the most recent posting timestamp for a platform.

    Args:
        platform: Platform name (e.g., 'mastodon')

    Returns:
        Most recent created_at from post_history, or None if never posted
    """
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT MAX(created_at) as last_posted FROM post_history 
            WHERE platform = $1 AND status = 'published'
        """,
            platform,
        )
        return row["last_posted"] if row and row["last_posted"] else None


async def posting_routine(dry_run: bool = False, max_items: int = 2):
    """
    Daily posting routine that processes verified Mastodon content.

    Args:
        dry_run: If True, skip actual publishing and log intent only
        max_items: Maximum number of items to post per execution
    """
    log_event("Starting posting routine", dry_run=dry_run, max_items=max_items)

    # Get verified content
    verified_items = await _get_verified_content(platform="mastodon")

    if not verified_items:
        log_event("No verified content available", level="info")
        return

    # Check last posted time for second item logic
    last_posted = await _get_last_posted_at(platform="mastodon")
    now = datetime.now(UTC)

    # Determine number of items to post
    items_to_post = []
    if max_items >= 1:
        items_to_post.append(verified_items[0])

        # Second item only if 8+ hours have passed since last posting
        # If never posted before (last_posted is None), only post 1 item
        if max_items >= 2 and last_posted is not None:
            if (now - last_posted) >= timedelta(hours=SECOND_POST_MIN_HOURS):
                if len(verified_items) > 1:
                    items_to_post.append(verified_items[1])
            else:
                log_event(
                    "Skipping second item - less than 8 hours since last post",
                    hours_since_last=(now - last_posted).total_seconds() / 3600,
                )

    log_event(
        "Items to post",
        count=len(items_to_post),
        item_ids=[item["id"] for item in items_to_post],
    )

    # Apply randomized delay between platform batches
    if len(items_to_post) > 0 and not dry_run:
        await _apply_randomized_delay()

    pool = await DatabaseClient.get_pool()
    for item in items_to_post:
        task_id = item["id"]
        prepared_content = item.get("prepared_content", {})

        # Handle string format from DB
        if isinstance(prepared_content, str):
            try:
                prepared_content = json.loads(prepared_content)
            except (json.JSONDecodeError, TypeError):
                prepared_content = {}

        if not prepared_content or not isinstance(prepared_content, dict):
            log_event(
                "Invalid prepared_content, skipping",
                level="warning",
                content_id=task_id,
            )
            continue

        content = prepared_content.get("mastodon", "")

        if dry_run:
            log_event(
                "Dry-run: would post content", content_id=task_id, platform="mastodon"
            )
            continue

        try:
            result = await publish_mastodon(content=content, task_id=task_id)

            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO post_history (
                        content_id, platform, status, published_url
                    ) VALUES ($1, $2, 'published', $3)
                    ON CONFLICT (content_id, platform)
                    DO UPDATE
                    SET status = 'published', published_url = $3, error_log = NULL
                    """,
                    task_id,
                    "mastodon",
                    result.get("url", ""),
                )

            log_event(
                "Content posted successfully",
                task_id=task_id,
                platform="mastodon",
                result=result,
            )

        except Exception as e:
            log_event(
                f"Failed to post content: {str(e)}",
                level="error",
                task_id=task_id,
                error=str(e),
            )

            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO post_history (
                        content_id, platform, status, error_log
                    ) VALUES ($1, $2, 'failed', $3)
                    ON CONFLICT (content_id, platform)
                    DO UPDATE SET status = 'failed', error_log = $3
                    """,
                    task_id,
                    "mastodon",
                    str(e),
                )


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    max_items = 2

    # Parse max_items if provided
    for arg in sys.argv:
        if arg.startswith("--max-items="):
            max_items = int(arg.split("=")[1])

    asyncio.run(posting_routine(dry_run=dry_run, max_items=max_items))
