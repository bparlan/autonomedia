import asyncio
import logging
import json
import structlog
from src.database.client import DatabaseClient
from src.autonomedia.platforms.mastodon.task_handler import publish_mastodon

# Structured JSON logging
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()

class PostingWorker:
    def __init__(self):
        self.interval = 30 # seconds

    async def run(self):
        logger.info("executor_started")
        while True:
            await self.process_prepared_content()
            await asyncio.sleep(self.interval)

    async def process_prepared_content(self):
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            # Fetch prepared items
            rows = await conn.fetch("SELECT * FROM content WHERE status = 'prepared'")
            
            for row in rows:
                task_id = row['id']
                try:
                    prepared_data = json.loads(row['prepared_content'])
                    content = prepared_data['content']
                    
                    logger.info("posting_content", task_id=task_id)
                    
                    # Execute via Mastodon handler
                    result = await publish_mastodon(content=content, task_id=task_id)
                    
                    # Transition to published
                    await conn.execute("UPDATE content SET status = 'published' WHERE id = $1", task_id)
                    logger.info("content_published", task_id=task_id, result=result)

                except Exception as e:
                    logger.error("posting_failed", task_id=task_id, error=str(e))
                    await conn.execute("UPDATE content SET status = 'failed', error_log = $1 WHERE id = $2", str(e), task_id)

if __name__ == "__main__":
    worker = PostingWorker()
    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        logger.info("executor_stopped")
