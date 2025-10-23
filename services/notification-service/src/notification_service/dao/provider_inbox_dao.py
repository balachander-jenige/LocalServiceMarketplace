from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.provider_inbox import ProviderInbox


class ProviderInboxDAO:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["provider_inbox"]

    async def create(self, notification: ProviderInbox) -> ProviderInbox:
        await self.collection.insert_one(notification.model_dump())
        return notification

    async def get_by_provider_id(self, provider_id: int) -> List[ProviderInbox]:
        cursor = self.collection.find({"provider_id": provider_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [ProviderInbox(**{k: v for k, v in doc.items() if k != "_id"}) for doc in docs]

    async def mark_as_read(self, provider_id: int, order_id: int):
        await self.collection.update_many(
            {"provider_id": provider_id, "order_id": order_id}, {"$set": {"is_read": True}}
        )
