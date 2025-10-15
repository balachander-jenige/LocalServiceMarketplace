from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProviderProfile(BaseModel):
    """服务商资料 MongoDB 模型"""
    user_id: int = Field(..., description="用户 ID（来自 Auth Service）")
    skills: List[str] = Field(default_factory=list, description="技能列表")
    experience_years: int = Field(default=0)
    hourly_rate: float = Field(default=0.0)
    availability: Optional[str] = None
    portfolio: List[str] = Field(default_factory=list, description="作品集 URLs")
    total_earnings: float = Field(default=0.0, description="总收入")
    rating: float = Field(default=5.0, description="平均评分")
    total_reviews: int = Field(default=0, description="评价总数")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 2,
                "skills": ["Python", "FastAPI", "MongoDB"],
                "experience_years": 5,
                "hourly_rate": 50.0,
                "availability": "Full-time",
                "portfolio": ["https://example.com/project1"],
                "total_earnings": 5000.0,
                "rating": 4.8,
                "total_reviews": 20
            }
        }