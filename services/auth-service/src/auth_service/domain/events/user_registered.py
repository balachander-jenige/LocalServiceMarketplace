from pydantic import BaseModel
from datetime import datetime

class UserRegisteredEvent(BaseModel):
    """用户注册事件"""
    user_id: int
    username: str
    email: str
    role_id: int
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }