import asyncio
import logging
import json
import structlog
from src.database.client import DatabaseClient
from src.autonomedia.ai.rewriting.gemini import GeminiProvider
from src.autonomedia.ai.moderation import ModerationAdapter, ModerationError
from src.autonomedia.content.transforms.entity_normalizer import EntityNormalizer
from src.autonomedia.ai.rewriting.context import RewriteContext

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
        self.normalizer = EntityNormalizer()
        self.interval = 30  # seconds

    async def run(self):
        logger.info("secretary_started", interval=self.interval)
        while True:
            await self.process_approved_content()
            await asyncio.sleep(self.interval)

    async def process_approved_content(self):
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
                task_id = row['id']
                logger.info("processing_content", task_id=task_id)
                
                try:
                    # Determine target platforms
                    platforms_raw = row.get('platforms')
                    platforms = json.loads(platforms_raw) if platforms_raw and platforms_raw != '[]' else ['mastodon']
                    
                    if platforms == ['all']:
                        platforms = list(ModerationAdapter.PLATFORM_LIMITS.keys())
                    
                    prepared_data = {}
                    for platform in platforms:
                        # Fetch platform limits
                        limit = ModerationAdapter.PLATFORM_LIMITS.get(platform, {}).get("max_chars", 500)
                        
                        prompt = (
                            f"Rewrite for {platform}. Provide EXACTLY one final post. "
                            f"Do not include multiple options or explanations. "
                            f"Must be under {limit} characters. "
                            "POLICY: Use registered entity tags for known companies/brands if available in your internal knowledge. "
                            "If you are unsure of an official tag, use plain text name only. Do not hallucinate tags."
                        )

                        # Construct Context
                        context = RewriteContext(
                            source_idea=row['source_idea'],
                            platform=platform
                        )
                        
                        rewritten = await self.provider.rewrite(
                            context=context, 
                            prompt=prompt
                        )
                        
                        # Post-process with EntityNormalizer for deterministic compliance
                        rewritten = self.normalizer.normalize_text(rewritten, platform)
                        
                        # Validate immediately
                        ModerationAdapter.validate(platform, rewritten)
                        prepared_data[platform] = rewritten

                    # Transition to 'prepared' (Awaiting user review)
                    payload = json.dumps(prepared_data)
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
