from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Connection到 MongoDB"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client.get_database()
    print(f"✅ Connected to MongoDB: {settings.MONGODB_URL}")


async def close_mongo_connection():
    """关闭 MongoDB Connection"""
    if mongodb.client:
        mongodb.client.close()
        print("✅ Closed MongoDB connection")


def get_database():
    """GetDatabase实例"""
    return mongodb.db
