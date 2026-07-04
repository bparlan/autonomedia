import asyncio
import os

import asyncpg


async def migrate():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia"))

    # 1. Add settings table for Policy Engine
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    # 2. Insert default settings
    await conn.execute("""
        INSERT INTO settings (key, value) VALUES 
        ('max_posts_per_day', '2'),
        ('cooldown_hours', '6')
        ON CONFLICT (key) DO NOTHING;
    """)


    await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
