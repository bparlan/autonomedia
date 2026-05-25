import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
import asyncio
import asyncpg
from src.database.client import DatabaseClient
import os

# Deterministic test DB
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia_test")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_pool():
    """Provides a fresh database pool and cleans up state."""
    # Create a fresh pool per test to avoid event loop issues
    pool = await asyncpg.create_pool(os.getenv("DATABASE_URL", "postgresql://bparlan@localhost:5432/autonomedia"))
    # Reset critical tables
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE content RESTART IDENTITY CASCADE")
    yield pool
    await pool.close()

@pytest.fixture(scope="function")
async def clean_db(db_pool):
    """Alias for db_pool cleanup logic."""
    return db_pool
