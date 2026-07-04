# src/database/client.py
import os

import asyncpg

# Deterministic configuration via environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia"
)


class DatabaseClient:
    _pool = None

    @classmethod
    async def get_pool(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(DATABASE_URL)
        return cls._pool

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
