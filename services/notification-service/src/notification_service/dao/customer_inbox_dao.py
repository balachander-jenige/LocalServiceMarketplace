from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from ..models.customer_inbox import CustomerInbox

class CustomerInboxDAO:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["customer_inbox"]

    async def create(self, notification: CustomerInbox) -> CustomerInbox:
        await self.collection.insert_one(notification.model_dump())
        return notification

    async def get_by_customer_id(self, customer_id: int) -> List[CustomerInbox]:
        cursor = self.collection.find({"customer_id": customer_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [CustomerInbox(**{k: v for k, v in doc.items() if k != "_id"}) for doc in docs]

    async def mark_as_read(self, customer_id: int, order_id: int):
        await self.collection.update_many(
            {"customer_id": customer_id, "order_id": order_id},
            {"$set": {"is_read": True}}
        )