import asyncio
import asyncpg
import json

async def update():
    conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/autonomedia')
    await conn.execute("UPDATE content SET platforms = $1 WHERE id = $2", json.dumps(["mastodon", "x"]), "001")
    await conn.close()

asyncio.run(update())
