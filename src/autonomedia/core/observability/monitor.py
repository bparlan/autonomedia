import logging
import json
from datetime import datetime, timezone
from src.database.client import DatabaseClient
from src.autonomedia.core.observability.telegram import notifier

logger = logging.getLogger("passive_health_monitor")

class PassiveHealthMonitor:
    FAILURE_THRESHOLD = 3

    @classmethod
    async def run(cls):
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            platforms = ["mastodon", "x", "linkedin", "bluesky", "threads", "facebook_pages"]
            
            for platform in platforms:
                # 1. Fetch old status
                old_row = await conn.fetchrow("SELECT status FROM platform_health WHERE platform_name = $1", platform)
                old_status = old_row['status'] if old_row else 'uninitialized'

                # 2. Determine new status
                history = await conn.fetch(
                    "SELECT status FROM post_history WHERE platform = $1 ORDER BY created_at DESC LIMIT $2",
                    platform, cls.FAILURE_THRESHOLD
                )
                
                if not history:
                    status = 'uninitialized'
                elif len(history) >= cls.FAILURE_THRESHOLD and all(h['status'] == 'failed' for h in history):
                    status = 'unhealthy'
                else:
                    status = 'healthy'
                
                # 3. Update DB and notify on transition
                if status != old_status:
                    await conn.execute("""
                        INSERT INTO platform_health (platform_name, status, last_checked)
                        VALUES ($1, $2, NOW())
                        ON CONFLICT (platform_name) DO UPDATE 
                        SET status = EXCLUDED.status, last_checked = EXCLUDED.last_checked
                    """, platform, status)
                    
                    if status == 'unhealthy':
                        await notifier.notify(f"⚠️ Platform *{platform}* is UNHEALTHY! 3+ failures detected.")
                    elif status == 'healthy':
                        await notifier.notify(f"✅ Platform *{platform}* is back to HEALTHY.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(PassiveHealthMonitor.run())
