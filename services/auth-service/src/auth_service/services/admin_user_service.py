from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dao.role_dao import RoleDAO
from ..dao.user_dao import UserDAO
from ..models.user import User


class AdminUserService:
    """Admin User Management Service"""

    @staticmethod
    async def get_all_users(db: AsyncSession, role_id: Optional[int] = None) -> List[User]:
        """Get All Users List"""
        return await UserDAO.get_all_users(db, role_id)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        """Get User Details"""
        user = await UserDAO.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        role_id: Optional[int] = None,
    ) -> User:
        """Update User Information"""
        # Validate if role_id is valid
        if role_id is not None:
            role = await RoleDAO.get_role_by_id(db, role_id)
            if not role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role_id: {role_id}")

        user = await UserDAO.update_user(db, user_id, username=username, email=email, role_id=role_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Delete User"""
        success = await UserDAO.delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return True
