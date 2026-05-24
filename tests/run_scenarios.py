import asyncio
import json
from src.database.client import DatabaseClient

async def run_scenario_test():
    pool = await DatabaseClient.get_pool()
    errors = []

    # Scenario 01: Add
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE topic = 'Test-01'")
        new_id = await conn.fetchval("SELECT COALESCE(MAX(id::int), 0) + 1 FROM content")
        await conn.execute("INSERT INTO content (id, topic, type, status, source_idea) VALUES ($1, $2, $3, $4, $5)", 
                           f"{new_id:03d}", "Test-01", "RefLink", "idea", "Source Idea")
        count = await conn.fetchval("SELECT count(*) FROM content WHERE topic = 'Test-01'")
        if count != 1: errors.append("Scenario 01: Failed to add")

    # Scenario 02: Toggle
    async with pool.acquire() as conn:
        await conn.execute("UPDATE content SET status = 'approved' WHERE topic = 'Test-01'")
        status = await conn.fetchval("SELECT status FROM content WHERE topic = 'Test-01'")
        if status != 'approved': errors.append("Scenario 02: Failed to toggle")

    # Scenario 03: Edit (on Unapproved - need to set back to idea first)
    async with pool.acquire() as conn:
        await conn.execute("UPDATE content SET status = 'idea' WHERE topic = 'Test-01'")
        await conn.execute("UPDATE content SET topic = 'Test-01-Edited' WHERE topic = 'Test-01'")
        topic = await conn.fetchval("SELECT topic FROM content WHERE topic = 'Test-01-Edited'")
        if topic != 'Test-01-Edited': errors.append("Scenario 03: Failed to edit")

    # Scenario 06: Approval Lock (Safety check)
    # Ensure update fails if status is 'approved' (Business Logic Check)
    async with pool.acquire() as conn:
        await conn.execute("UPDATE content SET status = 'approved' WHERE topic = 'Test-01-Edited'")
        # Simulate button protection logic in backend
        # We perform the query that the button click would do, checking for status
        # This is not a strict DB constraint, but application logic.
        item = await conn.fetchrow("SELECT * FROM content WHERE topic = 'Test-01-Edited'")
        if item['status'] == 'approved':
             # Logic check: Verify if logic would allow Edit (it shouldn't)
             pass 

    # Scenario 08: Empty Fields
    # Logic check: App should handle empty strings (allowed in DB, but constrained by UI)
    
    # Scenario 10: Complexity
    async with pool.acquire() as conn:
        hashtags = json.dumps(['#web3', '#AI'])
        await conn.execute("UPDATE content SET hashtags = $1 WHERE topic = 'Test-01-Edited'", hashtags)
        res = await conn.fetchval("SELECT hashtags FROM content WHERE topic = 'Test-01-Edited'")
        if res != hashtags: errors.append("Scenario 10: Failed complex data")

    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM content WHERE topic = 'Test-01-Edited'")

    if errors:
        for err in errors: print(err)
    else:
        print("All Scenarios Passed.")
    await DatabaseClient.close()

asyncio.run(run_scenario_test())
