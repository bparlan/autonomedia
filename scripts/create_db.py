import asyncio
import asyncpg

async def create_db():
    try:
        # Connect to default database 'postgres' to issue CREATE DATABASE command
        # Note: CREATE DATABASE cannot be run inside a transaction
        conn = await asyncpg.connect('postgresql://bparlan@localhost:5432/postgres')
        await conn.execute('CREATE DATABASE autonomedia')
        print("Database 'autonomedia' created successfully.")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_db())
