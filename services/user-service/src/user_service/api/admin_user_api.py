from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from ..core.mongodb import get_database
from ..core.dependencies import get_current_user_id
from ..services.admin_user_service import AdminUserService
from ..dto.admin_dto import (
    UserSummary,
    UserDetailAdmin,
    UpdateUserRequest,
    DeleteUserResponse
)

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.get("", response_model=List[UserSummary])
async def get_all_users(
    role_id: Optional[int] = None,
    current_user_id: int = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """获取所有用户列表（管理员）"""
    # 注意: Gateway 层会验证管理员权限
    service = AdminUserService(db)
    users = await service.get_all_users(role_id)
    return users


@router.get("/{user_id}", response_model=UserDetailAdmin)
async def get_user_detail(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """获取用户详情（管理员）"""
    service = AdminUserService(db)
    user = await service.get_user_detail(user_id)
    return user


@router.put("/{user_id}", response_model=UserDetailAdmin)
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    current_user_id: int = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """更新用户信息（管理员）"""
    service = AdminUserService(db)
    await service.update_user(
        user_id,
        username=request.username,
        email=request.email,
        role_id=request.role_id
    )
    # 更新后重新获取用户详情
    user = await service.get_user_detail(user_id)
    return user


@router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """删除用户（管理员）"""
    service = AdminUserService(db)
    success = await service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return DeleteUserResponse(
        user_id=user_id,
        message="User deleted successfully"
    )
