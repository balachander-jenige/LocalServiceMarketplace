from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

from ..dao.provider_profile_dao import ProviderProfileDAO
from ..models.provider_profile import ProviderProfile
from ..domain.events.profile_created import ProfileCreatedEvent
from ..domain.events.profile_updated import ProfileUpdatedEvent
from ..events.publishers.event_publisher import EventPublisher

class ProviderProfileService:
    """服务商资料服务"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.dao = ProviderProfileDAO(db)
    
    async def create_profile(
        self,
        user_id: int,
        skills: List[str] = None,
        experience_years: int = 0,
        hourly_rate: float = 0.0,
        availability: str = None
    ):
        """创建服务商资料"""
        existing = await self.dao.get_by_user_id(user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider profile already exists"
            )
        
        profile = ProviderProfile(
            user_id=user_id,
            skills=skills or [],
            experience_years=experience_years,
            hourly_rate=hourly_rate,
            availability=availability,
            portfolio=[],
            # total_earnings 字段已删除 - 第三阶段修改
            rating=5.0,
            total_reviews=0
        )
        
        created_profile = await self.dao.create(profile)
        
        # 发布事件
        event = ProfileCreatedEvent(
            user_id=user_id,
            profile_type="provider",
            timestamp=datetime.utcnow()
        )
        await EventPublisher.publish_profile_created(event)
        
        return created_profile
    
    async def get_profile(self, user_id: int):
        """获取服务商资料"""
        profile = await self.dao.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider profile not found"
            )
        return profile
    
    async def update_profile(self, user_id: int, update_data: dict):
        """更新服务商资料"""
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to update"
            )
        
        profile = await self.dao.update(user_id, update_data)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider profile not found"
            )
        
        # 发布事件
        event = ProfileUpdatedEvent(
            user_id=user_id,
            profile_type="provider",
            updated_fields=update_data,
            timestamp=datetime.utcnow()
        )
        await EventPublisher.publish_profile_updated(event)
        
        return profile
    
    async def search_providers(
        self,
        skills: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        max_hourly_rate: Optional[float] = None,
        limit: int = 20
    ):
        """搜索服务商"""
        return await self.dao.search_providers(
            skills=skills,
            min_rating=min_rating,
            max_hourly_rate=max_hourly_rate,
            limit=limit
        )