import asyncio

from src.database.client import DatabaseClient


async def main():
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM content')


if __name__ == '__main__':
    asyncio.run(main())
