from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..dto.user_dto import DeleteUserResponse, UpdateUserRequest, UserResponse
from ..services.admin_user_service import AdminUserService

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.get("", response_model=List[UserResponse])
async def get_all_users(role_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Get All Users List（Admin）"""
    # Note: Gateway Layer Has VerifiedAdminPermission，This Is Internal Service Call
    users = await AdminUserService.get_all_users(db, role_id)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_detail(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get User Details（Admin）"""
    # Note: Gateway Layer Has VerifiedAdminPermission，This Is Internal Service Call
    user = await AdminUserService.get_user_by_id(db, user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, request: UpdateUserRequest, db: AsyncSession = Depends(get_db)):
    """Update User Information（Admin）"""
    # Note: Gateway Layer Has VerifiedAdminPermission，This Is Internal Service Call
    user = await AdminUserService.update_user(
        db, user_id, username=request.username, email=request.email, role_id=request.role_id
    )
    return user


@router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete User（Admin）"""
    # Note: Gateway Layer Has VerifiedAdminPermission，This Is Internal Service Call
    await AdminUserService.delete_user(db, user_id)

    return DeleteUserResponse(user_id=user_id, message="User deleted successfully")
