import os
import asyncpg
from fastapi import HTTPException

# Fallback to defaults if not set
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "face-recognition-db")

pool = None

async def get_pool():
    global pool
    if pool is None:
        try:
            pool = await asyncpg.create_pool(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            raise e
    return pool

async def execute_query(query, *args):
    p = await get_pool()
    async with p.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute_non_query(query, *args):
    p = await get_pool()
    async with p.acquire() as conn:
        return await conn.execute(query, *args)

async def init_db():
    # Create table if not exists
    # We assume vector extension is already enabled in AlloyDB
    create_table_query = """
    CREATE TABLE IF NOT EXISTS face_embeddings (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        image_uri TEXT,
        embedding vector(3072)
    );
    """
    try:
        await execute_non_query(create_table_query)
        print("Database initialized.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        # We might not have permission to create table, or extension might be missing
        # But we proceed assuming it might work or table already exists
        pass
