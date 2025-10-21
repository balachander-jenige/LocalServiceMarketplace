from pydantic import BaseModel
from datetime import datetime

class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    role_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenVerifyResponse(BaseModel):
    """Token 验证响应"""
    user_id: int
    role_id: int
    username: str
    email: str