from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.role import Role


class RoleDAO:
    """RoleData Access Object"""

    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: int) -> Role | None:
        """By ID GetRole"""
        return await db.get(Role, role_id)

    @staticmethod
    async def get_role_by_name(db: AsyncSession, role_name: str) -> Role | None:
        """ByName称GetRole"""
        result = await db.execute(select(Role).where(Role.role_name == role_name))
        return result.scalars().first()
