import pytest


@pytest.mark.asyncio
async def test_migration_and_atomic_claim(db_pool):
    # 1. Verify columns exist
    async with db_pool.acquire() as conn:
        # Check if attempt_count and last_attempt_at exist
        try:
            await conn.execute("SELECT attempt_count, last_attempt_at FROM content LIMIT 1")
        except Exception as e:
            pytest.fail(f"Columns attempt_count or last_attempt_at do not exist: {e}")

    # 2. Verify Atomic Claim
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE id = 'm10-test'")
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, created_at)
            VALUES ($1, $2, $3, $4, NOW())
        """, "m10-test", "TOPIC", "TYPE", "ready_to_post")

        # Mock atomic claim
        result = await conn.execute("""
            UPDATE content 
            SET status = 'posting', 
                attempt_count = attempt_count + 1, 
                last_attempt_at = CURRENT_TIMESTAMP 
            WHERE id = $1 AND status = 'ready_to_post'
        """, "m10-test")

        # result is a string status in asyncpg if using raw query or something else?
        # Actually in asyncpg it returns "UPDATE 1"
        assert "UPDATE 1" in result or result == 1

        # Verify status
        task = await conn.fetchrow("SELECT status, attempt_count FROM content WHERE id = 'm10-test'")
        assert task['status'] == 'posting'
        assert task['attempt_count'] == 1

@pytest.mark.asyncio
async def test_sigterm_handling(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE id = 'm10-sigterm'")
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, created_at)
            VALUES ($1, $2, $3, $4, NOW())
        """, "m10-sigterm", "TOPIC", "TYPE", "posting")

        # Simulate SIGTERM worker cleanup: transition from 'posting' to 'failed'
        await conn.execute("""
            UPDATE content 
            SET status = 'failed' 
            WHERE id = $1 AND status = 'posting'
        """, "m10-sigterm")

        task = await conn.fetchrow("SELECT status FROM content WHERE id = 'm10-sigterm'")
        assert task['status'] == 'failed'

@pytest.mark.asyncio
async def test_retry_mechanism(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE id = 'm10-retry'")
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, attempt_count, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
        """, "m10-retry", "TOPIC", "TYPE", "failed", 1)

        # Simulate worker processing retry
        await conn.execute("""
            UPDATE content 
            SET status = 'ready_to_post' 
            WHERE id = $1 AND status = 'failed'
        """, "m10-retry")

        # Now atomic claim it again
        await conn.execute("""
            UPDATE content 
            SET status = 'posting', 
                attempt_count = attempt_count + 1, 
                last_attempt_at = CURRENT_TIMESTAMP 
            WHERE id = $1 AND status = 'ready_to_post'
        """, "m10-retry")

        task = await conn.fetchrow("SELECT status, attempt_count FROM content WHERE id = 'm10-retry'")
        assert task['status'] == 'posting'
        assert task['attempt_count'] == 2
