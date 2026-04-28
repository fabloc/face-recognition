import os
import asyncpg
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            logger.info(f"Attempting to create connection pool for host={DB_HOST}, db={DB_NAME}, user={DB_USER}")
            pool = await asyncpg.create_pool(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                ssl='require'
            )
            logger.info("Connection pool created successfully.")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise e
    return pool

async def execute_query(query, *args):
    logger.info(f"Executing query: {query} with args: {args}")
    p = await get_pool()
    try:
        async with p.acquire() as conn:
            results = await conn.fetch(query, *args)
            logger.info(f"Query executed successfully. Returned {len(results)} rows.")
            return results
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise e

async def execute_non_query(query, *args):
    logger.info(f"Executing non-query: {query} with args: {args}")
    p = await get_pool()
    try:
        async with p.acquire() as conn:
            result = await conn.execute(query, *args)
            logger.info(f"Non-query executed successfully. Result: {result}")
            return result
    except Exception as e:
        logger.error(f"Non-query execution failed: {e}")
        raise e

async def init_db():
    logger.info("Initializing database...")
    try:
        # Create extension if not exists
        await execute_non_query("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            image_uri TEXT,
            embedding vector(3072)
        );
        """
        await execute_non_query(create_table_query)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e
