from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserSummary(BaseModel):
    """用户摘要（管理员视图）"""
    user_id: int
    username: str
    email: str
    role_id: int
    role_name: str
    has_profile: bool
    created_at: datetime

class UserDetailAdmin(BaseModel):
    """用户详情（管理员视图）"""
    user_id: int
    username: str
    email: str
    role_id: int
    role_name: str
    profile: Optional[dict] = None  # 客户或服务商资料
    created_at: datetime

class UpdateUserRequest(BaseModel):
    """管理员更新用户请求"""
    username: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None

class DeleteUserResponse(BaseModel):
    """删除用户响应"""
    user_id: int
    message: str
