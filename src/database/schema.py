# src/database/schema.py

INIT_SCHEMA = """
CREATE TABLE IF NOT EXISTS content (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    source_idea TEXT,
    link_url TEXT,
    hashtags JSONB DEFAULT '[]',
    mentions JSONB DEFAULT '{}',
    ai_rewrites JSONB DEFAULT '[]',
    prepared_content JSONB DEFAULT '{}',
    platforms JSONB DEFAULT '[]',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    error_log TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS platform_health (
    platform_name TEXT PRIMARY KEY,
    is_healthy BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_status TEXT,
    error_message TEXT
);
"""
