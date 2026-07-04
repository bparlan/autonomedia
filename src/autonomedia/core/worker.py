import asyncio
import json
import logging
import signal
import sys
from datetime import UTC, datetime
from pathlib import Path

from src.autonomedia.database.client import DatabaseClient

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from autonomedia.core.logger import log_post_event
from autonomedia.platforms.mastodon.task_handler import publish_mastodon

# Setup structured logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("worker")

MAX_RETRIES = 3

from src.autonomedia.core.error_resolver import ErrorResolver

# ... existing code ...

MAX_RETRIES = 3

error_resolver = ErrorResolver()

# Platform Registry
PLATFORM_HANDLERS = {
    "mastodon": publish_mastodon,
}


async def is_platform_halted(platform):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        status = await conn.fetchval(
            "SELECT status FROM platform_health WHERE platform_name = $1", platform
        )
        return status == "halted"


async def execute_task(task):
    """Executes the task logic with platform routing via registry."""
    task_dict = dict(task) if not isinstance(task, dict) else task

    content = task_dict.get("prepared_content")
    platform = task_dict.get("platform", "mastodon")
    task_id = task_dict.get("id")

    # Halt check
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        platform_rec = await conn.fetchrow(
            "SELECT is_paused FROM platforms WHERE name = $1", platform
        )
        if platform_rec and platform_rec["is_paused"]:
            logger.info(f"Skipping {task_id}: Platform {platform} is PAUSED.")
            return

    # Legacy Halt check
    if await is_platform_halted(platform):
        logger.info(f"Skipping {task_id}: Platform {platform} is HALTED.")
        return

    handler = PLATFORM_HANDLERS.get(platform)
    if not handler:
        raise ValueError(f"Unknown platform: {platform}")

    return await handler(content, task_id)


async def worker(name, queue, stop_event):
    """
    Generic worker that consumes tasks from the queue with retry logic.
    """
    while not stop_event.is_set():
        try:
            task = await asyncio.wait_for(queue.get(), timeout=1.0)
        except TimeoutError:
            continue

        task_id = task.get("id")
        platform = task.get("platform", "mastodon")

        logger.info(
            json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "info",
                    "message": f"Worker {name} started task",
                    "task_id": task_id,
                }
            )
        )

        start_time = datetime.now()

        for attempt in range(MAX_RETRIES):
            try:
                await execute_task(task)

                duration = (datetime.now() - start_time).total_seconds()
                await log_post_event(task_id, platform, "success", duration=duration)

                # Mark as 'posted' in DB
                pool = await DatabaseClient.get_pool()
                async with pool.acquire() as conn:
                    await conn.execute(
                        "UPDATE content SET status = 'posted' WHERE id = $1", task_id
                    )

                logger.info(
                    json.dumps(
                        {
                            "timestamp": datetime.now(UTC).isoformat(),
                            "level": "info",
                            "message": "Task success",
                            "task_id": task_id,
                        }
                    )
                )
                break
            except Exception as e:
                # Artifact capture
                import os

                try:
                    os.makedirs("storage/screenshots", exist_ok=True)
                    # Assuming we have some way to trigger browser screenshot if context exists,
                    # but spec says 'deterministic path resolution'
                    with open(f"storage/screenshots/{task_id}.png", "wb") as f:
                        f.write(b"placeholder")
                    with open(f"storage/dom/{task_id}.html", "w") as f:
                        f.write("<html></html>")
                except Exception as artifact_err:
                    logger.error(f"Artifact capture failed: {artifact_err}")

                last_error = str(e)
                error_type = error_resolver.classify(e)

                logger.warning(
                    json.dumps(
                        {
                            "timestamp": datetime.now(UTC).isoformat(),
                            "level": "warning",
                            "message": f"Task attempt {attempt + 1} failed",
                            "error": last_error,
                            "task_id": task_id,
                            "type": error_type,
                        }
                    )
                )

                if error_type == "fatal":
                    logger.info(
                        f"Fatal error detected for {task_id}, skipping retries."
                    )
                    break

                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                else:
                    duration = (datetime.now() - start_time).total_seconds()
                    await log_post_event(
                        task_id,
                        platform,
                        "failed",
                        error_log=last_error,
                        duration=duration,
                    )

                    # Mark as 'failed' in DB
                    pool = await DatabaseClient.get_pool()
                    async with pool.acquire() as conn:
                        await conn.execute(
                            "UPDATE content SET status = 'failed', error_log = $1 WHERE id = $2",
                            last_error,
                            task_id,
                        )
                        await conn.execute(
                            "UPDATE platforms SET failure_count = failure_count + 1 WHERE name = $1",
                            platform,
                        )
                        # Check circuit breaker
                        res = await conn.fetchval(
                            "SELECT failure_count FROM platforms WHERE name = $1",
                            platform,
                        )
                        if res and res >= 3:
                            await conn.execute(
                                "UPDATE platforms SET is_paused = TRUE WHERE name = $1",
                                platform,
                            )
                            logger.error(f"Circuit breaker triggered for {platform}")

                    logger.error(
                        json.dumps(
                            {
                                "timestamp": datetime.now(UTC).isoformat(),
                                "level": "error",
                                "message": "Task failed after max retries",
                                "task_id": task_id,
                            }
                        )
                    )

        queue.task_done()
        logger.info(
            json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "info",
                    "message": f"Worker {name} finished task",
                    "task_id": task_id,
                }
            )
        )


async def poller(queue, stop_event):
    """Polls database for ready tasks."""
    logger.info("Poller started")
    while not stop_event.is_set():
        try:
            pool = await DatabaseClient.get_pool()
            async with pool.acquire() as conn:
                task = await conn.fetchrow("""
                    UPDATE content 
                    SET status = 'posting',
                        attempt_count = attempt_count + 1,
                        last_attempt_at = CURRENT_TIMESTAMP
                    WHERE id = (
                        SELECT id FROM content 
                        WHERE status = 'ready_to_post' 
                        ORDER BY created_at ASC 
                        FOR UPDATE SKIP LOCKED 
                        LIMIT 1
                    )
                    RETURNING *
                """)

                if task:
                    logger.info(f"Poller found task: {task['id']}")
                    queue.put_nowait(task)

        except Exception as e:
            logger.error(f"Poller error: {e}")

        await asyncio.sleep(10)


async def main():
    queue = asyncio.Queue()
    stop_event = asyncio.Event()

    # Signal handling
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    # Start poller and worker
    poller_task = asyncio.create_task(poller(queue, stop_event))
    worker_task = asyncio.create_task(worker("1", queue, stop_event))

    # Wait for stop event
    await stop_event.wait()

    # Graceful shutdown
    logger.info("Shutdown signaled, cleaning up...")

    # Cancel tasks
    poller_task.cancel()
    worker_task.cancel()

    # Wait for cancellation
    await asyncio.gather(poller_task, worker_task, return_exceptions=True)

    logger.info("Worker system successfully shut down")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
