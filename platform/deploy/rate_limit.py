import os, aioredis
from fastapi_limiter import FastAPILimiter

async def setup_rate_limit():
    redis = await aioredis.from_url(os.getenv("REDIS_URL","redis://localhost:6379"), encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
