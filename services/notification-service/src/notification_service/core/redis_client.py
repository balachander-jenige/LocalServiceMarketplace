import redis.asyncio as redis
from .config import settings

class RedisClient:
    client: redis.Redis = None

redis_client = RedisClient()

async def connect_to_redis():
    redis_client.client = await redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    print(f"✅ Connected to Redis: {settings.REDIS_URL}")

async def close_redis_connection():
    if redis_client.client:
        await redis_client.client.close()
        print("✅ Closed Redis connection")

def get_redis():
    return redis_client.client