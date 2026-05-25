import pytest
import asyncio
import json
import logging
from unittest.mock import AsyncMock, patch
from src.database.client import DatabaseClient
from src.autonomedia.core.worker import worker, poller, PLATFORM_HANDLERS

logger = logging.getLogger("test_worker")

@pytest.mark.asyncio
async def test_worker_flow(db_pool):
    """
    Integration test:
    1. Insert task into DB as 'ready_to_post'.
    2. Start worker and poller.
    3. Mock the posting function.
    4. Verify state transitions.
    """
    queue = asyncio.Queue()
    stop_event = asyncio.Event()

    # 1. Setup
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, platforms, created_at) 
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
        """, "t-1", "TEST-WORKER", "TestType", "ready_to_post", json.dumps("Test Content"), json.dumps(["mastodon"]))

    # 2. Mock Posting
    mock_post = AsyncMock(return_value={"status": "success"})
    
    # Patch the registry directly
    with patch.dict(PLATFORM_HANDLERS, {"mastodon": mock_post}):
        
        # 3. Run components
        poller_task = asyncio.create_task(poller(queue, stop_event))
        worker_task = asyncio.create_task(worker("TEST", queue, stop_event))
        
        # Give it a moment to pick up
        await asyncio.sleep(2)
        
        # 4. Signal Stop
        stop_event.set()
        await asyncio.gather(poller_task, worker_task)

        # 5. Verify
        async with db_pool.acquire() as conn:
            task = await conn.fetchrow("SELECT status FROM content WHERE topic = 'TEST-WORKER'")
            status = task['status']
            
            assert status == 'published'
            mock_post.assert_called_once()
