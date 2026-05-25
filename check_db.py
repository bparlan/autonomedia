import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    rows = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'content'")
    for row in rows:
        print(f"{row['column_name']}: {row['data_type']}")
    await conn.close()

asyncio.run(check())
