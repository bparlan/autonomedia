import asyncio

from src.autonomedia.database.client import DatabaseClient
from src.autonomedia.database.schema import INIT_SCHEMA


async def update():
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(INIT_SCHEMA)


asyncio.run(update())
