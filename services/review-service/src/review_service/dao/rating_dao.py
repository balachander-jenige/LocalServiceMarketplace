from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.rating import ProviderRating


class RatingDAO:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["provider_ratings"]

    async def get_by_provider_id(self, provider_id: int) -> Optional[ProviderRating]:
        doc = await self.collection.find_one({"provider_id": provider_id})
        if doc:
            doc.pop("_id", None)
            return ProviderRating(**doc)
        return None

    async def upsert_rating(self, provider_id: int, average_rating: float, total_reviews: int) -> ProviderRating:
        await self.collection.update_one(
            {"provider_id": provider_id},
            {"$set": {"average_rating": average_rating, "total_reviews": total_reviews}},
            upsert=True,
        )
        return ProviderRating(provider_id=provider_id, average_rating=average_rating, total_reviews=total_reviews)
