from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .security import verify_token

async def get_current_user_id(token_data: dict = Depends(verify_token)) -> int:
    """从 Token 中获取当前用户 ID"""
    user_id = token_data.get("sub")
    if not user_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    return int(user_id)