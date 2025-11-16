from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.customer_profile import CustomerProfile


class CustomerProfileDAO:
    """CustomerProfileData Access Object"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["customer_profiles"]

    async def create(self, profile: CustomerProfile) -> CustomerProfile:
        """CreateCustomerProfile"""
        profile_dict = profile.model_dump()
        await self.collection.insert_one(profile_dict)
        return profile

    async def get_by_user_id(self, user_id: int) -> Optional[CustomerProfile]:
        """ByUser ID GetCustomerProfile"""
        doc = await self.collection.find_one({"user_id": user_id})
        if doc:
            doc.pop("_id", None)  # 移除 MongoDB _id
            return CustomerProfile(**doc)
        return None

    async def update(self, user_id: int, update_data: dict) -> Optional[CustomerProfile]:
        """UpdateCustomerProfile"""
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.update_one({"user_id": user_id}, {"$set": update_data})

        if result.modified_count > 0:
            return await self.get_by_user_id(user_id)
        return None

    async def delete(self, user_id: int) -> bool:
        """DeleteCustomerProfile"""
        result = await self.collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0
