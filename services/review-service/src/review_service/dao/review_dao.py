from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.review import Review


class ReviewDAO:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["reviews"]

    async def create(self, review: Review) -> Review:
        await self.collection.insert_one(review.model_dump())
        return review

    async def get_by_order_id(self, order_id: int) -> Optional[Review]:
        doc = await self.collection.find_one({"order_id": order_id})
        if doc:
            doc.pop("_id", None)
            return Review(**doc)
        return None

    async def get_reviews_for_provider(self, provider_id: int) -> List[Review]:
        cursor = self.collection.find({"provider_id": provider_id})
        docs = await cursor.to_list(length=100)
        return [Review(**{k: v for k, v in doc.items() if k != "_id"}) for doc in docs]
