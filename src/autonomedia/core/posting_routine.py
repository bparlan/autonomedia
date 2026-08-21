# src/autonomedia/core/posting_routine.py
"""
Daily Posting Routine with Randomized Intervals (M15S1) - Updated with Platform Abstraction Layer
"""

import asyncio
import json
import random
from datetime import UTC, datetime, timedelta

import structlog

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
        platform: Platform name (e.g., 'mastodon', 'linkedin', 'x')

    Returns:
        List of content rows that are verified and ready to post
    """
    from src.autonomedia.core.utils.verification import (
        get_verified_at_timestamp,
        is_platform_verified,
        parse_verification_status,
    )
    from src.autonomedia.database.client import DatabaseClient

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
        platform: Platform name (e.g., 'mastodon', 'linkedin', 'x')

    Returns:
        Most recent created_at from post_history, or None if never posted
    """
    from src.autonomedia.database.client import DatabaseClient

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
    Daily posting routine that processes verified content using the unified platform abstraction layer.

    Args:
        dry_run: If True, skip actual publishing and log intent only
        max_items: Maximum number of items to post per execution
    """
    log_event("Starting posting routine", dry_run=dry_run, max_items=max_items)

    # Get supported platforms from platform abstraction layer
    from src.autonomedia.core.platform import get_supported_platforms

    platforms = get_supported_platforms()
    
    if not platforms:
        log_event("No platforms are available for posting", level="warning")
        return

    # Process each platform
    for platform in platforms:
        log_event(
            f"Processing platform: {platform}",
            platform=platform,
            dry_run=dry_run,
        )

        # Get verified content
        verified_items = await _get_verified_content(platform=platform)

        if not verified_items:
            log_event(
                f"No verified content available for {platform}",
                level="info",
                platform=platform,
            )
            continue
        
        # Check last posted time for second item logic
        last_posted = await _get_last_posted_at(platform=platform)
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
                        f"Skipping second item - less than {SECOND_POST_MIN_HOURS} hours since last post",
                        hours_since_last=(now - last_posted).total_seconds() / 3600,
                        platform=platform,
                    )

        log_event(
            f"Items to post for {platform}",
            count=len(items_to_post),
            item_ids=[item["id"] for item in items_to_post],
            platform=platform,
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
                    platform=platform,
                )
                continue

            content = prepared_content.get(platform, "")

            if dry_run:
                log_event(
                    f"Dry-run: would post content to {platform}",
                    content_id=task_id,
                    platform=platform,
                )
                continue
            
            try:
                # Use unified platform API
                from src.autonomedia.core.platform import post as unified_post
                
                # Prepare options for unified platform API
                post_options = {
                    "platform": platform,
                    "browser_data_dir": "./runtime/browser_profiles",
                    "task_id": str(task_id),
                }

                # Call unified platform API
                result = await unified_post(content=content, options=post_options)

                if result["status"] == "success":
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
                            platform,
                            result.get("result", {}).get("url", ""),
                        )

                    log_event(
                        f"Content posted successfully to {platform}",
                        task_id=task_id,
                        platform=platform,
                        result=result,
                    )
                else:
                    log_event(
                        f"Failed to post content to {platform}",
                        level="error",
                        task_id=task_id,
                        platform=platform,
                        error=result.get("error", "Unknown error"),
                    )

                    async with pool.acquire() as conn:
                        await conn.execute(
                            """
                            INSERT INTO post_history (
                                content_id, platform, status, error_log
                            ) VALUES ($1, $2, 'error', $3)
                            ON CONFLICT (content_id, platform)
                            DO UPDATE
                            SET status = 'error', error_log = $3
                            """,
                            task_id,
                            platform,
                            result.get("error", "Unknown error"),
                        )

            except Exception as e:
                log_event(
                    f"Failed to post content to {platform}: {str(e)}",
                    level="error",
                    task_id=task_id,
                    platform=platform,
                    error=str(e),
                )

                async with pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO post_history (
                            content_id, platform, status, error_log
                        ) VALUES ($1, $2, 'error', $3)
                        ON CONFLICT (content_id, platform)
                        DO UPDATE
                        SET status = 'error', error_log = $3
                        """,
                        task_id,
                        platform,
                        str(e),
                    )


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv
    max_items = 2

    # Parse max_items from command line
    for i, arg in enumerate(sys.argv):
        if arg == "--max-items" and i + 1 < len(sys.argv):
            try:
                max_items = int(sys.argv[i + 1])
            except ValueError:
                pass
    
    asyncio.run(posting_routine(dry_run=dry_run, max_items=max_items))
