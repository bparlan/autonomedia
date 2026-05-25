import asyncio
import asyncpg
import os

async def check():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia"))
    rows = await conn.fetch("SELECT * FROM platform_health")
    for row in rows:
        print(f"Platform: {row['platform_name']}, Healthy: {row['is_healthy']}")
    await conn.close()

asyncio.run(check())
