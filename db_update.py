import asyncio
from src.database.client import DatabaseClient
from src.database.schema import INIT_SCHEMA

async def update():
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(INIT_SCHEMA)
    print("DB Updated")

asyncio.run(update())
