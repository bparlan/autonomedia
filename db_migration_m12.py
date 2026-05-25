import asyncio
import asyncpg
import os

async def migrate():
    # Use standard connection string or env var
    conn = await asyncpg.connect("postgresql://bparlan@localhost:5432/autonomedia")
    await conn.execute("""
        ALTER TABLE content 
        ADD COLUMN IF NOT EXISTS verification_status JSONB DEFAULT '{}'::jsonb;
    """)
    print("Migration complete: verification_status column added to content table.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
