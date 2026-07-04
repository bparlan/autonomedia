import asyncio
import json
import logging
from unittest.mock import patch

import pytest

from src.autonomedia.core.worker import poller, worker
from src.database.client import DatabaseClient

logger = logging.getLogger("test_worker")

@pytest.mark.asyncio
async def test_worker_flow():
    queue = asyncio.Queue()
    stop_event = asyncio.Event()

    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE id = $1", "t-1")
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, platforms, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
        """, "t-1", "TEST-WORKER", "TestType", "ready_to_post",
            json.dumps("Test Content"), json.dumps(["mastodon"]))

    with patch("src.autonomedia.core.worker.PLATFORM_HANDLERS", {"mastodon": mock_post}) as mock_post:

        poller_task = asyncio.create_task(poller(queue, stop_event))
        worker_task = asyncio.create_task(worker("TEST", queue, stop_event))
        await asyncio.sleep(2)
        stop_event.set()
        await asyncio.gather(poller_task, worker_task)

    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        task = await conn.fetchrow("SELECT status FROM content WHERE topic = 'TEST-WORKER'")
        assert task["status"] == "published"
    mock_post.assert_called_once()
