from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProviderProfileCreate(BaseModel):
    """创建服务商资料请求"""
    skills: List[str] = []
    experience_years: int = 0
    hourly_rate: float = 0.0
    availability: Optional[str] = None

class ProviderProfileUpdate(BaseModel):
    """更新服务商资料请求"""
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability: Optional[str] = None
    portfolio: Optional[List[str]] = None

class ProviderProfileResponse(BaseModel):
    """服务商资料响应"""
    user_id: int
    skills: List[str]
    experience_years: int
    hourly_rate: float
    availability: Optional[str]
    portfolio: List[str]
    # total_earnings 字段已删除 - 第三阶段修改
    rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True