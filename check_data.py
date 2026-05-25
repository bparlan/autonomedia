import asyncio
import asyncpg
import json

async def check():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    rows = await conn.fetch('SELECT id, prepared_content FROM content WHERE prepared_content IS NOT NULL')
    for row in rows:
        print(f"ID {row['id']}: {row['prepared_content']} (Type: {type(row['prepared_content'])})")
    await conn.close()

asyncio.run(check())
