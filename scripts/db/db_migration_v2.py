import asyncio
import os

import asyncpg


async def migrate():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia"))

    # Drop old column and recreate with status enum-like behavior
    await conn.execute("DROP TABLE IF EXISTS platform_health")
    await conn.execute("""
        CREATE TABLE platform_health (
            platform_name TEXT PRIMARY KEY,
            status TEXT DEFAULT 'uninitialized', 
            last_checked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        );
    """)


    await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
