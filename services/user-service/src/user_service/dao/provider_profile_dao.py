from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from datetime import datetime
from ..models.provider_profile import ProviderProfile

class ProviderProfileDAO:
    """服务商资料数据访问对象"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["provider_profiles"]
    
    async def create(self, profile: ProviderProfile) -> ProviderProfile:
        """创建服务商资料"""
        profile_dict = profile.model_dump()
        await self.collection.insert_one(profile_dict)
        return profile
    
    async def get_by_user_id(self, user_id: int) -> Optional[ProviderProfile]:
        """根据用户 ID 获取服务商资料"""
        doc = await self.collection.find_one({"user_id": user_id})
        if doc:
            doc.pop("_id", None)
            return ProviderProfile(**doc)
        return None
    
    async def update(self, user_id: int, update_data: dict) -> Optional[ProviderProfile]:
        """更新服务商资料"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_by_user_id(user_id)
        return None
    
    async def delete(self, user_id: int) -> bool:
        """删除服务商资料"""
        result = await self.collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0
    
    async def search_providers(
        self,
        skills: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        max_hourly_rate: Optional[float] = None,
        limit: int = 20
    ) -> List[ProviderProfile]:
        """搜索服务商"""
        query = {}
        
        if skills:
            query["skills"] = {"$in": skills}
        if min_rating is not None:
            query["rating"] = {"$gte": min_rating}
        if max_hourly_rate is not None:
            query["hourly_rate"] = {"$lte": max_hourly_rate}
        
        cursor = self.collection.find(query).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        profiles = []
        for doc in docs:
            doc.pop("_id", None)
            profiles.append(ProviderProfile(**doc))
        
        return profiles