# scripts/ingest_content.py
import asyncio
import csv
import json
import sys
import os
import re
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.database.client import DatabaseClient
from src.database.schema import INIT_SCHEMA

async def ingest_csv(csv_path: Path):
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.")
        return

    pool = await DatabaseClient.get_pool()
    
    # Initialize Schema (Dropping old schema to apply the Assembly Line v2 schema)
    async with pool.acquire() as conn:
        await conn.execute("DROP TABLE IF EXISTS content;")
        await conn.execute(INIT_SCHEMA)
        print("Database schema dropped and recreated for Assembly Line (v2).")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if count >= 5:
                break
            
            if not row.get('id') or not row.get('post_text'):
                continue

            post_text = row['post_text']
            
            # Extract Data from legacy flat text
            url_match = re.search(r'(https?://[^\s]+)', post_text)
            link_url = url_match.group(1) if url_match else ""
            
            hashtags = list(set(re.findall(r'#(\w+)', post_text)))
            hashtags_formatted = [f"#{t}" for t in hashtags]
            
            mentions_list = list(set(re.findall(r'@(\w+)', post_text)))
            mentions = {"default": [f"@{m}" for m in mentions_list]} if mentions_list else {}
            
            # Remove the URL line from the text to isolate the idea
            source_idea = re.sub(r'⬇\s*https?://[^\s]+', '', post_text).strip()

            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO content (id, topic, type, status, source_idea, link_url, hashtags, mentions)
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb)
                """, row['id'], row['topic'], row['type'], row['status'], source_idea, link_url, json.dumps(hashtags_formatted), json.dumps(mentions))
            
            print(f"Ingested: {row['id']} - Isolated components successfully.")
            count += 1

    await DatabaseClient.close()

if __name__ == "__main__":
    csv_file = Path("docs/autonomedia-db-content-1.csv")
    asyncio.run(ingest_csv(csv_file))
