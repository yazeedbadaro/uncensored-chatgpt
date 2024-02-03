from fastapi import FastAPI
from .database import *
from contextlib import asynccontextmanager
from .routers import chat,user,auth,model
from fastapi_limiter import FastAPILimiter
import redis.asyncio as rs

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    redis = rs.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
    yield
    del model,tokenizer,redis
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(chat.router,prefix="/v1")
app.include_router(user.router,prefix="/v1")
app.include_router(model.router,prefix="/v1")
app.include_router(auth.router)

@app.get("/")
async def root():
    return "hello world"
