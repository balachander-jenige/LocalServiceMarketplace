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
    # Auth Service 字段
    username: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None
    
    # Customer Profile 字段
    location: Optional[str] = None  # NORTH, SOUTH, EAST, WEST, MID
    address: Optional[str] = None
    budget_preference: Optional[float] = None
    
    # Provider Profile 字段
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability: Optional[str] = None
    portfolio: Optional[List[str]] = None

class DeleteUserResponse(BaseModel):
    """删除用户响应"""
    user_id: int
    message: str
