import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    statuses = await conn.fetch("SELECT DISTINCT status FROM content")
    print([s['status'] for s in statuses])
    await conn.close()

asyncio.run(main())
