from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from ..dao.user_dao import UserDAO

class UserService:
    """用户服务"""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        """获取用户信息"""
        user = await UserDAO.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user