from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    """User响应"""

    id: int
    username: str
    email: str
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TokenVerifyResponse(BaseModel):
    """Token Verify响应"""

    user_id: int
    role_id: int
    username: str
    email: str


class UpdateUserRequest(BaseModel):
    """AdminUpdateUser请求"""

    username: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None


class DeleteUserResponse(BaseModel):
    """Delete User响应"""

    user_id: int
    message: str
