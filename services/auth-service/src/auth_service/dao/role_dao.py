from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.role import Role


class RoleDAO:
    """角色数据访问对象"""

    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: int) -> Role | None:
        """根据 ID 获取角色"""
        return await db.get(Role, role_id)

    @staticmethod
    async def get_role_by_name(db: AsyncSession, role_name: str) -> Role | None:
        """根据名称获取角色"""
        result = await db.execute(select(Role).where(Role.role_name == role_name))
        return result.scalars().first()
