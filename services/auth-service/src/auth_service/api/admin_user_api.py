from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..services.admin_user_service import AdminUserService
from ..dto.user_dto import (
    UserResponse,
    UpdateUserRequest,
    DeleteUserResponse
)

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.get("", response_model=List[UserResponse])
async def get_all_users(
    role_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取所有用户列表（管理员）"""
    # 注意: Gateway 层已验证管理员权限，这是内部服务调用
    users = await AdminUserService.get_all_users(db, role_id)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情（管理员）"""
    # 注意: Gateway 层已验证管理员权限，这是内部服务调用
    user = await AdminUserService.get_user_by_id(db, user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息（管理员）"""
    # 注意: Gateway 层已验证管理员权限，这是内部服务调用
    user = await AdminUserService.update_user(
        db,
        user_id,
        username=request.username,
        email=request.email,
        role_id=request.role_id
    )
    return user


@router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除用户（管理员）"""
    # 注意: Gateway 层已验证管理员权限，这是内部服务调用
    success = await AdminUserService.delete_user(db, user_id)
    
    return DeleteUserResponse(
        user_id=user_id,
        message="User deleted successfully"
    )
