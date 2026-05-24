import asyncio
import asyncpg
import sys
from pathlib import Path

# Fix path to ensure src/ is importable
sys.path.append(str(Path(__file__).parent.parent))

from src.database.schema import INIT_SCHEMA

async def migrate():
    # Connect to your existing database
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    
    # Add new columns if they don't exist
    commands = [
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS prepared_content JSONB DEFAULT '{}';",
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP WITH TIME ZONE;",
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS error_log TEXT;"
    ]
    
    for cmd in commands:
        try:
            await conn.execute(cmd)
            print(f"Executed: {cmd}")
        except Exception as e:
            print(f"Skipped/Error on '{cmd}': {e}")
            
    await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
