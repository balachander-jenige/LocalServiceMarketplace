from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomerProfileCreate(BaseModel):
    """创建客户资料请求"""
    location: str = "NORTH"
    address: Optional[str] = None
    budget_preference: float = 0.0

class CustomerProfileUpdate(BaseModel):
    """更新客户资料请求"""
    location: Optional[str] = None
    address: Optional[str] = None
    budget_preference: Optional[float] = None
    # balance 字段已删除 - 第三阶段修改

class CustomerProfileResponse(BaseModel):
    """客户资料响应"""
    user_id: int
    location: str
    address: Optional[str]
    budget_preference: float
    # balance 字段已删除 - 第三阶段修改
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True