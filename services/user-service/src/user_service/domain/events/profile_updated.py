from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class ProfileUpdatedEvent(BaseModel):
    """用户资料更新事件"""
    user_id: int
    profile_type: str  # "customer" or "provider"
    updated_fields: Dict[str, Any]
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }