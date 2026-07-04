import asyncio
import sys
from pathlib import Path

import asyncpg

# Fix path to ensure src/ is importable
sys.path.append(str(Path(__file__).parent.parent.parent))

async def migrate():
    # Connect to your existing database
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    
    # Add new columns
    commands = [
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS attempt_count INT DEFAULT 0;",
        "ALTER TABLE content ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMP WITH TIME ZONE;"
    ]
    
    for cmd in commands:
        try:
            await conn.execute(cmd)
            
        except Exception as e:
            
            
    await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
