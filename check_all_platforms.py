import asyncio
import asyncpg
import json

async def check():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    rows = await conn.fetch('SELECT id, platforms FROM content')
    for row in rows:
        print(f"ID {row['id']}: {row['platforms']} (Type: {type(row['platforms'])})")
    await conn.close()

asyncio.run(check())
