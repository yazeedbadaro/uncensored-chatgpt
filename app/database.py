from fastapi import Depends
import aiomysql
from aiomysql import create_pool
import os

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await create_pool(
            host=os.environ.get("DATABASE_HOSTNAME"), 
            port=int(os.environ.get("DATABASE_PORT")),
            user=os.environ.get("DATABASE_USERNAME"), 
            password=os.environ.get("DATABASE_PASSWORD"), 
            db=os.environ.get("DATABASE_NAME"),
            autocommit=True
        )

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

db = Database()

def get_db():
    return db.pool

async def execute_query(query, params=None, db=Depends(get_db)):
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchall()


