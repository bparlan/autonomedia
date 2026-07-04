import asyncio

import asyncpg


async def check():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    rows = await conn.fetch(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = 'content'"
    )
    for row in rows:
        await conn.close()
        await conn.close()

asyncio.run(check())
