import asyncio
import os

import asyncpg


async def migrate():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia"))
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS platform_health (
            platform_name TEXT PRIMARY KEY,
            is_healthy BOOLEAN DEFAULT TRUE,
            last_checked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            session_status TEXT,
            error_message TEXT
        );
    """)

    await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
