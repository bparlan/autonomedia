# Ensure src is in the python path for shared fixtures like db_pool
import sys
from pathlib import Path

import pytest

# Removed uvicorn import because of jinja2 dependency issues

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.client import DatabaseClient

# Commenting out live_server as it currently has dependency issues
# and isn't needed for the integration tests of the runtime.
# @pytest.fixture(scope="session", autouse=True)
# def live_server():
#     ...

@pytest.fixture(scope="function")
async def db_pool():
    """Provides a database connection pool for tests."""
    # Reset pool for each test to avoid loop issues
    DatabaseClient._pool = None
    pool = await DatabaseClient.get_pool()
    yield pool
    # We don't close the pool here to avoid interference with other tests
    # relying on the same DatabaseClient if any, but since we reset it,
    # we should probably close it.
    await DatabaseClient.close()
