from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..dto.user_dto import TokenVerifyResponse, UserResponse
from ..services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """获取当前用户信息"""
    user = await UserService.get_user_by_id(db, user_id)
    return UserResponse.from_orm(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取指定用户信息"""
    user = await UserService.get_user_by_id(db, user_id)
    return UserResponse.from_orm(user)


@router.get("/verify/token", response_model=TokenVerifyResponse)
async def verify_token_endpoint(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """验证 Token 并返回用户信息 (供其他服务调用)"""
    user = await UserService.get_user_by_id(db, user_id)
    return TokenVerifyResponse(user_id=user.id, role_id=user.role_id, username=user.username, email=user.email)
