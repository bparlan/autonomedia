import asyncio
import sys
from pathlib import Path

import asyncpg

# Ensure src/ is importable
sys.path.append(str(Path(__file__).parent.parent.parent))

async def migrate():
    # Connect to your existing database
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')

    # Add new columns to platforms table
    commands = [
        "CREATE TABLE IF NOT EXISTS platforms (id SERIAL PRIMARY KEY, name TEXT UNIQUE, failure_count INT DEFAULT 0, is_paused BOOLEAN DEFAULT FALSE);",
        "ALTER TABLE platforms ADD COLUMN IF NOT EXISTS failure_count INT DEFAULT 0;",
        "ALTER TABLE platforms ADD COLUMN IF NOT EXISTS is_paused BOOLEAN DEFAULT FALSE;"
    ]

    for cmd in commands:
        try:
            await conn.execute(cmd)

        except Exception:
            pass
            await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate())
