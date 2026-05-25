from src.database.client import DatabaseClient

async def log_post_event(content_id: str, platform: str, status: str, error_log: str = None, published_url: str = None, duration: float = None):
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO post_history (content_id, platform, status, error_log, published_url, execution_duration)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (content_id, platform) DO UPDATE 
            SET status = EXCLUDED.status, 
                error_log = EXCLUDED.error_log, 
                published_url = EXCLUDED.published_url,
                execution_duration = EXCLUDED.execution_duration,
                created_at = CURRENT_TIMESTAMP
        """, content_id, platform, status, error_log, published_url, duration)
