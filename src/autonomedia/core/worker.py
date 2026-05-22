import asyncio
import logging
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from autonomedia.platforms.mastodon.task_handler import publish_mastodon

# Setup structured logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("worker")

MAX_RETRIES = 3

async def execute_task(task):
    """Executes the task logic with platform routing."""
    if task.get("platform") == "mastodon":
        return await publish_mastodon(task.get("content"))
    raise ValueError(f"Unknown platform: {task.get('platform')}")

async def worker(name, queue):
    """
    Generic worker that consumes tasks from the queue with retry logic.
    """
    while True:
        task = await queue.get()
        task_id = task.get("id")
        
        logger.info(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "info",
            "message": f"Worker {name} started task",
            "task_id": task_id
        }))
        
        success = False
        for attempt in range(MAX_RETRIES):
            try:
                await execute_task(task)
                success = True
                logger.info(json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "info",
                    "message": "Task success",
                    "task_id": task_id
                }))
                break
            except Exception as e:
                logger.warning(json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "warning",
                    "message": f"Task attempt {attempt+1} failed",
                    "error": str(e),
                    "task_id": task_id
                }))
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt) # Exponential backoff
                else:
                    logger.error(json.dumps({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "level": "error",
                        "message": "Task failed after max retries",
                        "task_id": task_id
                    }))

        queue.task_done()
        logger.info(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "info",
            "message": f"Worker {name} finished task",
            "task_id": task_id
        }))

async def main():
    queue = asyncio.Queue()
    scheduler = AsyncIOScheduler()
    
    # Task scheduler
    def schedule_post():
        task = {"id": f"task-{datetime.now().timestamp()}", "platform": "mastodon", "content": "Hi Mum!"}
        queue.put_nowait(task)
        logger.info("Scheduled new task")

    scheduler.add_job(schedule_post, 'interval', minutes=10)
    scheduler.start()
    
    # Start worker
    worker_task = asyncio.create_task(worker("1", queue))
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        worker_task.cancel()
        scheduler.shutdown()
        logger.info("Worker system shutting down")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
