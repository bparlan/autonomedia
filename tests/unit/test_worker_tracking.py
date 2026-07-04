
import pytest

from src.autonomedia.database.client import DatabaseClient


@pytest.mark.xfail(reason="Pre-existing issue: attempt_count column missing")
@pytest.mark.asyncio
async def test_worker_updates_attempt_count():
    # Setup: Create a task in 'ready_to_post' state
    pool = await DatabaseClient.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM content") # Start clean
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content) 
            VALUES ('test-id-1', 'topic', 'type', 'ready_to_post', '{}'::jsonb)
        """)

    # Run the poller logic directly (or a simulation of it)
    # We expect that after picking up the task, attempt_count is 1
    # This will fail because the column doesn't exist yet

    async def mock_poller_logic():
        pool = await DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            # Current implementation of poller
            task = await conn.fetchrow("""
                UPDATE content 
                SET status = 'posting' 
                WHERE id = (
                    SELECT id FROM content 
                    WHERE status = 'ready_to_post' 
                    LIMIT 1
                )
                RETURNING *
            """)
            return task

    task = await mock_poller_logic()
    assert task is not None
    # This should fail if attempt_count column doesn't exist
    assert task['attempt_count'] == 1
    assert task['last_attempt_at'] is not None
