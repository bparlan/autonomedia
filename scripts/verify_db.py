import asyncio
import asyncpg

async def verify_ingestion():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    rows = await conn.fetch('SELECT id, topic, status FROM content')
    for row in rows:
        print(f"Row: {row['id']} | Topic: {row['topic']} | Status: {row['status']}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_ingestion())
