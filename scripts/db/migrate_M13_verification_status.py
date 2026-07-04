import asyncio
import os

import asyncpg


async def migrate():
    # Use environment variable for DB URL, or default
    db_url = os.getenv("DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia")


    conn = await asyncpg.connect(db_url)
    try:

        await conn.execute("""
            ALTER TABLE content 
            ADD COLUMN IF NOT EXISTS verification_status JSONB DEFAULT '{}'::jsonb
        """)

    except Exception:
            pass

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
