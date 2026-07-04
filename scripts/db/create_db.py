import asyncio

import asyncpg


async def create_db():
    try:
        # Connect to default database 'postgres' to issue CREATE DATABASE command
        # Note: CREATE DATABASE cannot be run inside a transaction
        conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/postgres')
        await conn.execute('CREATE DATABASE autonomedia')
    except Exception as e:
    except Exception as e:
        pass
