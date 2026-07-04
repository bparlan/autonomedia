import json

import pytest
from httpx import ASGITransport, AsyncClient

from src.database.schema import INIT_SCHEMA
from src.web.app import app


@pytest.fixture(autouse=True)
async def reset_db(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("DROP TABLE IF EXISTS content")
        await conn.execute("DROP TABLE IF EXISTS platform_health")
        await conn.execute(INIT_SCHEMA)

@pytest.mark.asyncio
async def test_rewrites_includes_ready_to_post(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content)
            VALUES ('100', 'Topic', 'blog', 'ready_to_post', '{}')
        """)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/rewrites")
    assert response.status_code == 200
    assert "Topic" in response.text

@pytest.mark.asyncio
async def test_prepared_content_endpoint(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content)
            VALUES ('101', 'Topic', 'blog', 'prepared', '{"mastodon": "hello"}')
        """)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/prepared-content/101")
    assert response.status_code == 200
    assert response.json() == {"mastodon": "hello"}

@pytest.mark.asyncio
async def test_approve_review_filters_healthy_platforms(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO platform_health (platform_name, is_healthy) VALUES ('mastodon', TRUE), ('twitter', FALSE)")
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content)
            VALUES ('102', 'Topic', 'blog', 'prepared', '{"mastodon": "m", "twitter": "t"}')
        """)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/review/102/approve", data={
            "action": "approve",
            "platform_mastodon": "m",
            "platform_twitter": "t",
            "verify_mastodon": "true",
            "verify_twitter": "true"
        })

    async with db_pool.acquire() as conn:
        item = await conn.fetchrow("SELECT verification_status FROM content WHERE id = '102'")
        status = json.loads(item['verification_status'])
        # Updated for M14S1: verification_status now contains dict with verified_at and expires_at
        assert status.get('mastodon', {}).get('verified') is True
        # Unhealthy platforms are removed from prepared_data, so they won't be in verification_status
        assert 'twitter' not in status or status.get('twitter', {}).get('verified') is False

@pytest.mark.asyncio
async def test_remove_from_queue_clears_verification(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content, verification_status)
            VALUES ('103', 'Topic', 'blog', 'ready_to_post', '{}', '{"mastodon": true}')
        """)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/remove-from-queue/103")
    assert response.status_code == 200

    async with db_pool.acquire() as conn:
        item = await conn.fetchrow("SELECT verification_status FROM content WHERE id = '103'")
        assert json.loads(item['verification_status']) == {}
        status_row = await conn.fetchval("SELECT status FROM content WHERE id = '103'")
        assert status_row == 'prepared'


# TC03: Invalid ID returns 404
@pytest.mark.asyncio
async def test_prepared_content_invalid_id_returns_404(db_pool):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/prepared-content/invalid-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# TC05: All unhealthy platforms returns 400
@pytest.mark.asyncio
async def test_approve_review_all_unhealthy_returns_400(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO platform_health (platform_name, is_healthy) VALUES ('mastodon', FALSE), ('twitter', FALSE)")
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content)
            VALUES ('104', 'Topic', 'blog', 'prepared', '{"mastodon": "m"}')
        """)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/review/104/approve", data={
            "action": "approve",
            "platform_mastodon": "m",
            "verify_mastodon": "true"
        })

    assert response.status_code == 400
    assert response.json()["detail"] == "No healthy platforms available"


# TC07: Concurrent approve calls return 409 Conflict
@pytest.mark.asyncio
async def test_concurrent_approve_returns_409(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO platform_health (platform_name, is_healthy) VALUES ('mastodon', TRUE)")
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content)
            VALUES ('105', 'Topic', 'blog', 'prepared', '{"mastodon": "m"}')
        """)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First request should succeed
        response1 = await client.post("/review/105/approve", data={
            "action": "approve",
            "platform_mastodon": "m1",
            "verify_mastodon": "true"
        })
        assert response1.status_code in (200, 303)

        # Second request should return 409 (item no longer in 'prepared' state)
        response2 = await client.post("/review/105/approve", data={
            "action": "approve",
            "platform_mastodon": "m2",
            "verify_mastodon": "true"
        })
    assert response2.status_code == 409
    assert "not in 'prepared' state" in response2.json()["detail"]


# TC08: Large payload (1 MiB) handling
@pytest.mark.asyncio
async def test_prepared_content_large_payload(db_pool):
    # Generate ~1 MiB of content
    large_text = "x" * (1024 * 1024)
    payload = json.dumps({"mastodon": large_text})

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content)
            VALUES ('106', 'Topic', 'blog', 'prepared', $1)
        """, payload)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/prepared-content/106")
    assert response.status_code == 200
    assert len(response.json()["mastodon"]) == 1024 * 1024


# TC09: Empty/null prepared_content handled gracefully
@pytest.mark.asyncio
async def test_prepared_content_empty_returns_empty_dict(db_pool):
    """Verify that empty prepared_content (NULL) returns empty dict instead of crashing."""
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO content (id, topic, type, status, prepared_content)
            VALUES ('107', 'Topic', 'blog', 'prepared', NULL)
        """)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/prepared-content/107")
    assert response.status_code == 200
    assert response.json() == {}
