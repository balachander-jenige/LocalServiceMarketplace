from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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


class UpdateUserRequest(BaseModel):
    """管理员更新用户请求"""

    username: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None


class DeleteUserResponse(BaseModel):
    """删除用户响应"""

    user_id: int
    message: str
