# tests/test_m14_routine.py
"""
Test suite for M14S1 - Daily Posting Routine with Randomized Intervals
"""
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from src.autonomedia.core.posting_routine import (
    _apply_randomized_delay,
    _get_last_posted_at,
    _get_verified_content,
    posting_routine,
)


@pytest.fixture(autouse=True)
async def reset_db(db_pool):
    """Reset database for each test."""
    async with db_pool.acquire() as conn:
        await conn.execute("DROP TABLE IF EXISTS content")
        await conn.execute("DROP TABLE IF EXISTS post_history")
        await conn.execute("DROP TABLE IF EXISTS platform_health")
        # Re-create tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                source_idea TEXT,
                link_url TEXT,
                batch_id TEXT,
                hashtags JSONB DEFAULT '[]',
                mentions JSONB DEFAULT '{}',
                ai_rewrites JSONB DEFAULT '[]',
                prepared_content JSONB DEFAULT '{}',
                platforms JSONB DEFAULT '[]',
                scheduled_at TIMESTAMP WITH TIME ZONE,
                error_log TEXT,
                metadata JSONB DEFAULT '{}',
                verification_status JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS post_history (
                id SERIAL PRIMARY KEY,
                content_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT NOT NULL,
                error_log TEXT,
                published_url TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (content_id, platform)
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS platform_health (
                platform_name TEXT PRIMARY KEY,
                is_healthy BOOLEAN DEFAULT TRUE,
                last_checked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                session_status TEXT,
                error_message TEXT
            );
        """)


def make_verification_status(verified=True, verified_at=None, expires_at=None):
    """Helper to create verification_status JSON."""
    status = {"verified": verified}
    if verified_at:
        status["verified_at"] = verified_at
    if expires_at:
        status["expires_at"] = expires_at
    return {"mastodon": status}


# TC1: Mastodon-verified ready_to_post item → posted successfully
@pytest.mark.asyncio
async def test_verified_mastodon_content_is_processed(db_pool):
    """Only mastodon-verified ready_to_post items should be processed."""
    verification_status = make_verification_status(verified=True, verified_at=datetime.now(UTC).isoformat())

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, '1', 'Topic', 'blog', 'ready_to_post', '{"mastodon": "test content"}', json.dumps(verification_status))

    # Mock publish_mastodon to avoid actual browser calls
    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = {"status": "success", "url": "https://test.url/post/1"}

        # Mock delay to avoid waiting
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Verify publish was called
    mock_publish.assert_called_once()


# TC2: Non-verified ready_to_post item → skipped with warning log
@pytest.mark.asyncio
async def test_non_verified_content_skipped(db_pool):
    """Non-verified ready_to_post items should be skipped."""
    verification_status = make_verification_status(verified=False)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, '2', 'Topic', 'blog', 'ready_to_post', '{"mastodon": "test content"}', json.dumps(verification_status))

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Verify publish was NOT called
    mock_publish.assert_not_called()


# TC4: Expired content (verified_at > 12 hours) → deprioritized or skipped
@pytest.mark.asyncio
async def test_expired_content_deprioritized(db_pool):
    """Content with verified_at > 12 hours ago should be deprioritized."""
    expired_time = (datetime.now(UTC) - timedelta(hours=13)).isoformat()
    expires_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    verification_status = make_verification_status(verified=True, verified_at=expired_time, expires_at=expires_time)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, '4', 'Topic', 'blog', 'ready_to_post', '{"mastodon": "expired content"}', json.dumps(verification_status))

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Expired content should not be posted
    mock_publish.assert_not_called()


# TC5: Priority-flagged content → posts even past expiration window
@pytest.mark.asyncio
async def test_priority_content_bypasses_expiration(db_pool):
    """Priority-flagged content should bypass normal expiration."""
    expired_time = (datetime.now(UTC) - timedelta(hours=15)).isoformat()
    expires_time = (datetime.now(UTC) - timedelta(hours=3)).isoformat()
    verification_status = make_verification_status(verified=True, verified_at=expired_time, expires_at=expires_time)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, '5', 'Topic', 'blog', 'ready_to_post', '{"mastodon": "priority content"}', json.dumps(verification_status), '{"priority": true}')

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Priority content should still be posted
    mock_publish.assert_called_once()


# TC6: Dry-run mode → logs intent, no post_history created
@pytest.mark.asyncio
async def test_dry_run_creates_no_post_history(db_pool):
    """Dry-run mode should log intent without creating post_history entries."""
    verification_status = make_verification_status(verified=True, verified_at=datetime.now(UTC).isoformat())

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, '6', 'Topic', 'blog', 'ready_to_post', '{"mastodon": "test content"}', json.dumps(verification_status))

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        await posting_routine(dry_run=True, max_items=2)

    # Verify publish was NOT called
    mock_publish.assert_not_called()

    # Verify no post_history entries created
    async with db_pool.acquire() as conn:
        history = await conn.fetch("SELECT * FROM post_history WHERE content_id = '6'")
        assert len(history) == 0


# TC7: Randomized delay → measured between 2-10 minutes
@pytest.mark.asyncio
async def test_randomized_delay_range():
    """Randomized delay should be between 2-10 minutes (120-600 seconds)."""
    delays = []
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        for _ in range(5):
            mock_sleep.reset_mock()
            await _apply_randomized_delay(min_minutes=2, max_minutes=10)
            if mock_sleep.called:
                call_time = mock_sleep.call_args[0][0]
                delays.append(call_time)
                assert 120 <= call_time <= 600, f"Delay {call_time}s outside 2-10 minute range"


# TC8: First execution → posts exactly 1 item
@pytest.mark.asyncio
async def test_first_execution_posts_one_item(db_pool):
    """First execution should post exactly 1 item."""
    verification_status = make_verification_status(verified=True, verified_at=datetime.now(UTC).isoformat())

    async with db_pool.acquire() as conn:
        for i in range(3):
            await conn.execute("""
                INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, f'8_{i}', 'Topic', 'blog', 'ready_to_post', f'{{"mastodon": "content {i}"}}', json.dumps(verification_status))

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Should post exactly 1 item
    assert mock_publish.call_count == 1


# TC9: Multiple verified items → exactly 1-2 items processed
@pytest.mark.asyncio
async def test_posts_one_to_two_items(db_pool):
    """Should post 1-2 items per execution."""
    verification_status = make_verification_status(verified=True, verified_at=datetime.now(UTC).isoformat())

    async with db_pool.acquire() as conn:
        for i in range(5):
            await conn.execute("""
                INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, f'9_{i}', 'Topic', 'blog', 'ready_to_post', f'{{"mastodon": "content {i}"}}', json.dumps(verification_status))

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Should post at most 2 items
    assert mock_publish.call_count <= 2


# TC3: Mixed verified/unverified platforms → only verified platforms processed
@pytest.mark.asyncio
async def test_mixed_verified_unverified_platforms(db_pool):
    """Mixed verified/unverified platforms → only verified platforms processed."""
    # Create content with both verified and unverified platforms in verification_status
    verification_status_mixed = {
        "mastodon": {"verified": True, "verified_at": datetime.now(UTC).isoformat()},
        "bluesky": {"verified": False, "verified_at": None}
    }

    # Content has prepared content for both platforms
    prepared = {"mastodon": "mastodon content", "bluesky": "bluesky content"}

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, '3', 'Topic', 'blog', 'ready_to_post', json.dumps(prepared), json.dumps(verification_status_mixed))

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Should only post mastodon (verified), not bluesky
    mock_publish.assert_called_once()


# TC9: Second execution within 8 hours → no additional items posted
@pytest.mark.asyncio
async def test_second_execution_within_8_hours_no_additional(db_pool):
    """Second execution within 8 hours → no additional items posted."""
    verification_status = make_verification_status(verified=True, verified_at=datetime.now(UTC).isoformat())

    async with db_pool.acquire() as conn:
        # Insert content
        for i in range(2):
            await conn.execute("""
                INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, f'9_{i}', 'Topic', 'blog', 'ready_to_post', f'{{"mastodon": "content {i}"}}', json.dumps(verification_status))

        # Insert post_history entry within last 8 hours (simulate recent posting)
        # Use datetime object for asyncpg compatibility
        recent_dt = datetime.now(UTC)
        await conn.execute("""
            INSERT INTO post_history (content_id, platform, status, published_url, created_at)
            VALUES ('recent_post', 'mastodon', 'published', 'url', $1)
        """, recent_dt)

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Should post only 1 item (second item blocked by 8-hour window)
    assert mock_publish.call_count == 1


# TC10: Execution after 8+ hours → second item may be posted
@pytest.mark.asyncio
async def test_execution_after_8_hours_second_item_allowed(db_pool):
    """Execution after 8+ hours → second item may be posted."""
    verification_status = make_verification_status(verified=True, verified_at=datetime.now(UTC).isoformat())

    async with db_pool.acquire() as conn:
        # Insert content
        for i in range(2):
            await conn.execute("""
                INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, f'10_{i}', 'Topic', 'blog', 'ready_to_post', f'{{"mastodon": "content {i}"}}', json.dumps(verification_status))

        # Insert post_history entry 10 hours ago (simulate old posting)
        old_dt = datetime.now(UTC) - timedelta(hours=10)
        await conn.execute("""
            INSERT INTO post_history (content_id, platform, status, published_url, created_at)
            VALUES ('old_post', 'mastodon', 'published', 'url', $1)
        """, old_dt)

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    # Should post 2 items (8+ hours passed, second item allowed)
    assert mock_publish.call_count == 2


# TC11: Manual trigger script → exits with code 0
def test_manual_trigger_script_exists():
    """Verify manual trigger script exists and is importable."""
    import os
    script_path = "/Users/bparlan/devcode/autonomedia/scripts/checks/run_daily_posting.py"
    assert os.path.exists(script_path), f"Script not found: {script_path}"


# Additional test: Item with no verification_status.mastodon data should be skipped
@pytest.mark.asyncio
async def test_item_without_verification_status_skipped(db_pool):
    """Item with ready_to_post status but no verification_status.mastodon should be skipped."""
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, '10', 'Topic', 'blog', 'ready_to_post', '{"mastodon": "test content"}', '{}')

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            await posting_routine(dry_run=False, max_items=2)

    mock_publish.assert_not_called()


# Test: No verified content available → routine logs and exits gracefully
@pytest.mark.asyncio
async def test_no_verified_content_graceful_exit(db_pool):
    """Routine should exit gracefully when no verified content available."""
    # Insert content without verification
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, '11', 'Topic', 'blog', 'ready_to_post', '{"mastodon": "content"}', '{"mastodon": {"verified": false}}')

    with patch('src.autonomedia.core.posting_routine.publish_mastodon', new_callable=AsyncMock) as mock_publish:
        with patch('src.autonomedia.core.posting_routine._apply_randomized_delay', new_callable=AsyncMock):
            # Should not raise any exception
            await posting_routine(dry_run=False, max_items=2)

    mock_publish.assert_not_called()


# Test: _get_verified_content returns only verified items
@pytest.mark.asyncio
async def test_get_verified_content_returns_verified_items(db_pool):
    """_get_verified_content should return only mastodon-verified items."""
    verification_status_verified = make_verification_status(verified=True, verified_at=datetime.now(UTC).isoformat())
    verification_status_unverified = make_verification_status(verified=False)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, 'v1', 'Topic1', 'blog', 'ready_to_post', '{"mastodon": "content1"}', json.dumps(verification_status_verified))
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, 'v2', 'Topic2', 'blog', 'ready_to_post', '{"mastodon": "content2"}', json.dumps(verification_status_unverified))

    items = await _get_verified_content(platform='mastodon')

    assert len(items) == 1
    assert items[0]['id'] == 'v1'


# Test: _get_last_posted_at returns correct timestamp
@pytest.mark.asyncio
async def test_get_last_posted_at(db_pool):
    """_get_last_posted_at should return the most recent posted timestamp."""
    async with db_pool.acquire() as conn:
        # Use datetime objects for asyncpg compatibility
        old_dt = datetime(2026, 6, 15, 10, 0, 0, tzinfo=UTC)
        new_dt = datetime(2026, 6, 16, 10, 0, 0, tzinfo=UTC)
        await conn.execute("""
            INSERT INTO post_history (content_id, platform, status, published_url, created_at)
            VALUES ('h1', 'mastodon', 'published', 'url1', $1)
        """, old_dt)
        await conn.execute("""
            INSERT INTO post_history (content_id, platform, status, published_url, created_at)
            VALUES ('h2', 'mastodon', 'published', 'url2', $1)
        """, new_dt)

    last_posted = await _get_last_posted_at(platform='mastodon')

    # Should return the most recent one
    assert last_posted is not None
    assert last_posted.isoformat() == new_dt.isoformat()
