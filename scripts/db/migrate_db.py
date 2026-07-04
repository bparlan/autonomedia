import asyncio
import sys
from pathlib import Path

import asyncpg

# Fix path to ensure src/ is importable
sys.path.append(str(Path(__file__).parent.parent))


async def migrate():
    # Connect to your existing database
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    
    # Add new columns if they don't exist
    commands = [
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS prepared_content JSONB DEFAULT '{}';",
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS platforms JSONB DEFAULT '[]';",
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP WITH TIME ZONE;",
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS error_log TEXT;",
        "ALTER TABLE post_history ADD COLUMN IF NOT EXISTS execution_duration FLOAT;"
    ]
    
    for cmd in commands:
        try:
            await conn.execute(cmd)
            
        except Exception as e:
            
            
    await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
