"""Async database operations for the minimal posting system."""
import asyncpg
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

DB_URL = "postgresql://bparlan@localhost:5432/autonomedia"

async def get_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(DB_URL)

async def init_db() -> asyncpg.Pool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Check if content table exists
        await conn.execute("
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                base_content TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending_rewrite',
                platforms JSONB DEFAULT '[]',
                verification_status JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                cooldown_hours FLOAT DEFAULT 168
            )
        ")
        await conn.execute("
            CREATE TABLE IF NOT EXISTS post_history (
                id SERIAL PRIMARY KEY,
                content_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT NOT NULL,
                error_log TEXT,
                published_url TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (content_id, platform)
            )
        ")
    return pool

async def store_idea(topic: str, base_content: str, platforms: List[str], cooldown_hours: float = 168) -> str:
    """Store a new idea and return its ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        idea_id = str(uuid.uuid4())
        await conn.execute("
            INSERT INTO content (id, topic, base_content, platforms, cooldown_hours)
            VALUES ($1, $2, $3, $4, $5)
        ", idea_id, topic, base_content, json.dumps(platforms), cooldown_hours)
        return idea_id

async def get_idea(idea_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve idea by ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("
            SELECT id, topic, base_content, status, platforms, verification_status, created_at, cooldown_hours
            FROM content
            WHERE id = $1
        ", idea_id)
        if not row:
            return None
        return dict(row)

async def update_idea_status(idea_id: str, status: str, verification_status: Optional[Dict] = None) -> None:
    """Update idea status and optionally verification_status."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        if verification_status is not None:
            await conn.execute("
                UPDATE content
                SET status = $2, verification_status = $3
                WHERE id = $1
            ", idea_id, status, json.dumps(verification_status))
        else:
            await conn.execute("
                UPDATE content
                SET status = $2
                WHERE id = $1
            ", idea_id, status)

async def set_verification(idea_id: str, platform: str, verified: bool, verified_at: Optional[datetime] = None) -> None:
    """Set verification status for a platform."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        current = await conn.fetchval("
            SELECT verification_status FROM content WHERE id = $1
        ", idea_id)
        current = json.loads(current) if current else {}
        current[platform] = {"verified": verified, "verified_at": verified_at.isoformat() if verified_at else None}
        await conn.execute("
            UPDATE content
            SET verification_status = $2
            WHERE id = $1
        ", idea_id, json.dumps(current))
        # If newly verified, bump status to ready_to_post if it's still pending_rewrite
        if verified:
            await conn.execute("
                UPDATE content
                SET status = 'ready_to_post'
                WHERE id = $1 AND status = 'pending_rewrite'
            ", idea_id)

async def get_ready_ideas() -> List[Dict[str, Any]]:
    """Get ideas that are ready_to_post for a platform (all platforms verified)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("
            SELECT id, topic, base_content, platforms, verification_status, cooldown_hours
            FROM content
            WHERE status = 'ready_to_post'
        ")
        ideas = []
        for row in rows:
            platforms = json.loads(row["platforms"]) if row["platforms"] else []
            verifications = json.loads(row["verification_status"]) if row["verification_status"] else {}
            ready = False
            for platform in platforms:
                if verifications.get(platform, {}).get("verified", False):
                    ready = True
                    break
            if ready:
                ideas.append(dict(row))
        return ideas

async def record_post(idea_id: str, platform: str, success: bool, url: Optional[str] = None, error: Optional[str] = None) -> None:
    """Record a posting attempt."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("
            INSERT INTO post_history (content_id, platform, status, error_log, published_url)
            VALUES ($1, $2, $3, $4, $5)
        ", idea_id, platform, "success" if success else "failed", error, url)

async def mark_posted(idea_id: str, platform: str, url: str) -> None:
    """Mark an idea as posted for a platform (update cooldown)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("
            UPDATE content
            SET status = 'posted'
            WHERE id = $1 AND platforms LIKE $2
        ", idea_id, "%%" || platform || "%%")
        await conn.execute("
            INSERT INTO post_history (content_id, platform, status, published_url)
            VALUES ($1, $2, 'posted', $3)
            ON CONFLICT (content_id, platform) DO UPDATE SET status = 'posted', published_url = $3
        ", idea_id, platform, url)
