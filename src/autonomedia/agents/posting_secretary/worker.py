import asyncio
import logging
import json
import structlog
from src.database.client import DatabaseClient
from src.autonomedia.ai.rewriting.gemini import GeminiProvider

# Structured JSON logging as per Autonomedia guidelines
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

class PostingSecretary:
    def __init__(self):
        self.provider = GeminiProvider()
        self.interval = 30  # seconds

    async def run(self):
        logger.info("secretary_started", interval=self.interval)
        while True:
            await self.process_approved_content()
            await asyncio.sleep(self.interval)

    async def process_approved_content(self):
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            # Atomic fetch to prevent double-processing in multi-worker setups
            rows = await conn.fetch("SELECT * FROM content WHERE status = 'approved'")
            
            for row in rows:
                task_id = row['id']
                logger.info("processing_content", task_id=task_id)
                
                try:
                    # AI Transformation
                    # Platform-specific prompt logic could be expanded here based on 'metadata'
                    rewritten = await self.provider.rewrite(
                        text=row['source_idea'], 
                        prompt="Rewrite for professional social media post."
                    )
                    
                    # Transition to 'prepared' - Wrap in JSON
                    payload = json.dumps({"content": rewritten})
                    await conn.execute("""
                        UPDATE content 
                        SET status = 'prepared', 
                            prepared_content = $1,
                            error_log = NULL
                        WHERE id = $2
                    """, payload, task_id)
                    
                    logger.info("content_prepared", task_id=task_id, status="success")
                    
                except Exception as e:
                    logger.error("content_preparation_failed", task_id=task_id, error=str(e))
                    await conn.execute("""
                        UPDATE content 
                        SET status = 'failed', 
                            error_log = $1 
                        WHERE id = $2
                    """, str(e), task_id)

if __name__ == "__main__":
    secretary = PostingSecretary()
    try:
        asyncio.run(secretary.run())
    except KeyboardInterrupt:
        logger.info("secretary_stopped")
