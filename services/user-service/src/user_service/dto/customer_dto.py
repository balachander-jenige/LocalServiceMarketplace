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
    balance: Optional[float] = None

class CustomerProfileResponse(BaseModel):
    """客户资料响应"""
    user_id: int
    location: str
    address: Optional[str]
    budget_preference: float
    balance: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True