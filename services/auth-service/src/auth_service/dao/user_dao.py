from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..models.user import User

class UserDAO:
    """用户数据访问对象"""
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        email: str,
        password_hash: str,
        role_id: int
    ) -> User:
        """创建用户"""
        from datetime import datetime, UTC
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role_id=role_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        db.add(user)
        
        try:
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail="用户名或邮箱已存在 / Username or email already exists"
            )
        
        return user
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """根据邮箱获取用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        """根据 ID 获取用户"""
        return await db.get(User, user_id)
    
    @staticmethod
    async def delete_user_by_username(db: AsyncSession, username: str) -> bool:
        """根据用户名删除用户"""
        from sqlalchemy import delete as sql_delete
        
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if user:
            await db.execute(sql_delete(User).where(User.id == user.id))
            await db.commit()
            return True
        return False