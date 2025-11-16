from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ProviderProfileCreate(BaseModel):
    """CreateProviderProfile请求"""

    skills: List[str] = []
    experience_years: int = 0
    hourly_rate: float = 0.0
    availability: Optional[str] = None


class ProviderProfileUpdate(BaseModel):
    """UpdateProviderProfile请求"""

    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability: Optional[str] = None
    portfolio: Optional[List[str]] = None


class ProviderProfileResponse(BaseModel):
    """ProviderProfile响应"""

    user_id: int
    skills: List[str]
    experience_years: int
    hourly_rate: float
    availability: Optional[str]
    portfolio: List[str]
    # total_earnings Field Removed - Phase 3 Modification
    rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
