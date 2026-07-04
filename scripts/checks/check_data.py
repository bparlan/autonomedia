import asyncio

import asyncpg


async def check():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    rows = await conn.fetch(
        'SELECT id, prepared_content FROM content WHERE prepared_content IS NOT NULL'
    )
    for row in rows:

        await conn.close()

asyncio.run(check())
