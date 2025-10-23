from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LocationEnum(str, Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    MID = "MID"


class CustomerProfile(BaseModel):
    """客户资料 MongoDB 模型"""

    user_id: int = Field(..., description="用户 ID（来自 Auth Service）")
    location: LocationEnum = Field(default=LocationEnum.NORTH)
    address: Optional[str] = None
    budget_preference: float = Field(default=0.0)
    # balance 字段已删除 - 第三阶段修改
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {"user_id": 1, "location": "NORTH", "address": "123 Main St", "budget_preference": 1000.0}
        }
