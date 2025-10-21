from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from datetime import datetime

from ..dao.customer_profile_dao import CustomerProfileDAO
from ..models.customer_profile import CustomerProfile, LocationEnum
from ..domain.events.profile_created import ProfileCreatedEvent
from ..domain.events.profile_updated import ProfileUpdatedEvent
from ..events.publishers.event_publisher import EventPublisher

class CustomerProfileService:
    """客户资料服务"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.dao = CustomerProfileDAO(db)
    
    async def create_profile(self, user_id: int, location: str, address: str = None, budget_preference: float = 0.0):
        """创建客户资料"""
        # 检查是否已存在
        existing = await self.dao.get_by_user_id(user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer profile already exists"
            )
        
        # 创建资料
        profile = CustomerProfile(
            user_id=user_id,
            location=LocationEnum(location),
            address=address,
            budget_preference=budget_preference
            # balance 字段已删除 - 第三阶段修改
        )
        
        created_profile = await self.dao.create(profile)
        
        # 发布事件
        event = ProfileCreatedEvent(
            user_id=user_id,
            profile_type="customer",
            timestamp=datetime.utcnow()
        )
        await EventPublisher.publish_profile_created(event)
        
        return created_profile
    
    async def get_profile(self, user_id: int):
        """获取客户资料"""
        profile = await self.dao.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )
        return profile
    
    async def update_profile(self, user_id: int, update_data: dict):
        """更新客户资料"""
        # 过滤 None 值
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
                detail="Customer profile not found"
            )
        
        # 发布事件
        event = ProfileUpdatedEvent(
            user_id=user_id,
            profile_type="customer",
            updated_fields=update_data,
            timestamp=datetime.utcnow()
        )
        await EventPublisher.publish_profile_updated(event)
        
        return profile