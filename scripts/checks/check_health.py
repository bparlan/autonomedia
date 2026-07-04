import asyncio
import os

import asyncpg


async def check():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia"))
    rows = await conn.fetch("SELECT * FROM platform_health")
    for row in rows:
        await conn.close()
        await conn.close()

asyncio.run(check())
