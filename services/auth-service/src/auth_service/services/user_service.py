from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dao.user_dao import UserDAO


class UserService:
    """User Service"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        """Get User Information"""
        user = await UserDAO.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
