import asyncio

import asyncpg


async def check():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    rows = await conn.fetch('SELECT id, platforms FROM content')
    for row in rows:
        await conn.close()

asyncio.run(check())
