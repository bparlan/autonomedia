"""
Add batch_id to content table.
"""

MIGRATION_ID = "m12_add_batch_id"

async def apply_migration(conn):
    await conn.execute("""
        ALTER TABLE content
        ADD COLUMN IF NOT EXISTS batch_id TEXT;
    """)


async def rollback_migration(conn):
    await conn.execute("""
        ALTER TABLE content
        DROP COLUMN IF EXISTS batch_id;
    """)

