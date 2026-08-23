
import asyncpg


async def check():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    row = await conn.fetchrow('SELECT platforms FROM content LIMIT 1')
    if row:
        pass  # Placeholder for if block
    else:
        pass  # Placeholder for else block
    await conn.close() # Correctly placed and indented
