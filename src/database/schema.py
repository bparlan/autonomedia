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
    scheduled_at TIMESTAMP WITH TIME ZONE,
    error_log TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""
