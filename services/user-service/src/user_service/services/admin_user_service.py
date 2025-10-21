import httpx
from fastapi import HTTPException, status
from typing import List, Optional
from ..core.config import settings
from ..dao.customer_profile_dao import CustomerProfileDAO
from ..dao.provider_profile_dao import ProviderProfileDAO


class AdminUserService:
    """管理员用户管理服务"""
    
    def __init__(self, db):
        self.db = db
        self.customer_dao = CustomerProfileDAO(db)
        self.provider_dao = ProviderProfileDAO(db)
    
    async def get_all_users(self, role_filter: Optional[int] = None) -> List[dict]:
        """获取所有用户列表（可按角色过滤）"""
        try:
            async with httpx.AsyncClient() as client:
                # 调用 Auth Service 获取用户列表
                url = f"{settings.AUTH_SERVICE_URL}/admin/users"
                params = {"role_id": role_filter} if role_filter else {}
                
                response = await client.get(url, params=params, timeout=10.0)
                
                if response.status_code == 200:
                    users = response.json()
                    
                    # 为每个用户添加 profile 状态
                    result = []
                    for user in users:
                        user_data = {
                            "user_id": user["id"],
                            "username": user["username"],
                            "email": user["email"],
                            "role_id": user["role_id"],
                            "role_name": self._get_role_name(user["role_id"]),
                            "has_profile": await self._check_profile_exists(user["id"], user["role_id"]),
                            "created_at": user.get("created_at")
                        }
                        result.append(user_data)
                    
                    return result
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to fetch users from Auth Service"
                    )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth Service unavailable: {str(e)}"
            )
    
    async def get_user_detail(self, user_id: int) -> dict:
        """获取用户详情（包含 Profile 信息）"""
        try:
            async with httpx.AsyncClient() as client:
                # 调用 Auth Service 获取用户基本信息
                url = f"{settings.AUTH_SERVICE_URL}/admin/users/{user_id}"
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to fetch user from Auth Service"
                    )
                
                user = response.json()
                
                # 获取用户的 Profile
                profile = None
                if user["role_id"] == 1:  # Customer
                    customer_profile = await self.customer_dao.get_by_user_id(user_id)
                    if customer_profile:
                        profile = customer_profile.model_dump(mode='json')
                elif user["role_id"] == 2:  # Provider
                    provider_profile = await self.provider_dao.get_by_user_id(user_id)
                    if provider_profile:
                        profile = provider_profile.model_dump(mode='json')
                
                return {
                    "user_id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role_id": user["role_id"],
                    "role_name": self._get_role_name(user["role_id"]),
                    "profile": profile,
                    "created_at": user.get("created_at")
                }
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth Service unavailable: {str(e)}"
            )
    
    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        role_id: Optional[int] = None
    ) -> dict:
        """更新用户信息"""
        try:
            update_data = {}
            if username:
                update_data["username"] = username
            if email:
                update_data["email"] = email
            if role_id is not None:
                update_data["role_id"] = role_id
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            async with httpx.AsyncClient() as client:
                url = f"{settings.AUTH_SERVICE_URL}/admin/users/{user_id}"
                response = await client.put(url, json=update_data, timeout=10.0)
                
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to update user"
                    )
                
                return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth Service unavailable: {str(e)}"
            )
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户（包括 Profile）"""
        try:
            # 1. 先删除用户的 Profile
            customer_profile = await self.customer_dao.get_by_user_id(user_id)
            if customer_profile:
                await self.customer_dao.delete(user_id)
            
            provider_profile = await self.provider_dao.get_by_user_id(user_id)
            if provider_profile:
                await self.provider_dao.delete(user_id)
            
            # 2. 调用 Auth Service 删除用户
            async with httpx.AsyncClient() as client:
                url = f"{settings.AUTH_SERVICE_URL}/admin/users/{user_id}"
                response = await client.delete(url, timeout=10.0)
                
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to delete user"
                    )
                
                return True
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth Service unavailable: {str(e)}"
            )
    
    async def _check_profile_exists(self, user_id: int, role_id: int) -> bool:
        """检查用户是否有 Profile"""
        if role_id == 1:  # Customer
            profile = await self.customer_dao.get_by_user_id(user_id)
            return profile is not None
        elif role_id == 2:  # Provider
            profile = await self.provider_dao.get_by_user_id(user_id)
            return profile is not None
        return False
    
    @staticmethod
    def _get_role_name(role_id: int) -> str:
        """获取角色名称"""
        role_names = {
            1: "customer",
            2: "provider",
            3: "admin"
        }
        return role_names.get(role_id, "unknown")
