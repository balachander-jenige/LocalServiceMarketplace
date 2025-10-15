from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..dto.auth_dto import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    user = await AuthService.register(
        db=db,
        username=data.username,
        email=data.email,
        password=data.password,
        role_id=data.role_id
    )
    return RegisterResponse(id=user.id, username=user.username, email=user.email)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    token = await AuthService.login(db, data.email, data.password)
    return TokenResponse(access_token=token)

@router.post("/logout")
async def logout():
    """用户登出"""
    return {"msg": "Logout successful"}