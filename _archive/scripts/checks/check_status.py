import asyncio

import asyncpg


async def main():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')


    await conn.close()

asyncio.run(main())
