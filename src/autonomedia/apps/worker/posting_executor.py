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
            # Fetch ready items (approved by user in dashboard)
            rows = await conn.fetch("SELECT * FROM content WHERE status = 'ready_to_post'")
            
            for row in rows:
                task_id = row['id']
                try:
                    prepared_data = json.loads(row['prepared_content'])
                    platforms_raw = row.get('platforms')
                    platforms = json.loads(platforms_raw) if platforms_raw and platforms_raw != '[]' else ['mastodon']
                    
                    for platform in platforms:
                        if platform not in prepared_data:
                            continue
                            
                        content = prepared_data[platform]
                        
                        # Check history to prevent duplicate
                        history = await conn.fetchrow(
                            "SELECT status FROM post_history WHERE content_id = $1 AND platform = $2",
                            task_id, platform
                        )
                        if history and history['status'] == 'published':
                            logger.info("skip_duplicate", task_id=task_id, platform=platform)
                            continue
                            
                        logger.info("posting_content", task_id=task_id, platform=platform)
                        
                        try:
                            # We only have mastodon handler right now
                            if platform == 'mastodon':
                                result = await publish_mastodon(content=content, task_id=task_id)
                                
                                await conn.execute("""
                                    INSERT INTO post_history (content_id, platform, status, published_url)
                                    VALUES ($1, $2, 'published', $3)
                                    ON CONFLICT (content_id, platform) 
                                    DO UPDATE SET status = 'published', published_url = $3, error_log = NULL
                                """, task_id, platform, result.get('url', ''))
                                
                                logger.info("content_published", task_id=task_id, platform=platform, result=result)
                            else:
                                logger.warning("unsupported_platform", platform=platform)
                        except Exception as e:
                            logger.error("platform_posting_failed", task_id=task_id, platform=platform, error=str(e))
                            await conn.execute("""
                                INSERT INTO post_history (content_id, platform, status, error_log)
                                VALUES ($1, $2, 'failed', $3)
                                ON CONFLICT (content_id, platform) 
                                DO UPDATE SET status = 'failed', error_log = $3
                            """, task_id, platform, str(e))
                            raise e # Propagate to fail the whole content item for now
                    
                    # Transition to published if all platforms succeed
                    await conn.execute("UPDATE content SET status = 'published' WHERE id = $1", task_id)

                except Exception as e:
                    logger.error("posting_failed", task_id=task_id, error=str(e))
                    await conn.execute("UPDATE content SET status = 'failed', error_log = $1 WHERE id = $2", str(e), task_id)

if __name__ == "__main__":
    worker = PostingWorker()
    try:
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        logger.info("executor_stopped")
