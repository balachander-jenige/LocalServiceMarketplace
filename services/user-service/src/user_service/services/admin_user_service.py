import logging
from typing import List, Optional

import httpx
from fastapi import HTTPException, status

from ..core.config import settings
from ..dao.customer_profile_dao import CustomerProfileDAO
from ..dao.provider_profile_dao import ProviderProfileDAO
from ..dto.admin_dto import UpdateUserRequest

logger = logging.getLogger(__name__)


class AdminUserService:
    """Admin User Management Service"""

    def __init__(self, db):
        self.db = db
        self.customer_dao = CustomerProfileDAO(db)
        self.provider_dao = ProviderProfileDAO(db)

    async def get_all_users(self, role_filter: Optional[int] = None) -> List[dict]:
        """Get All Users List（CanByRoleFilter）"""
        try:
            async with httpx.AsyncClient() as client:
                # Call Auth Service GetUserList
                url = f"{settings.AUTH_SERVICE_URL}/admin/users"
                params = {"role_id": role_filter} if role_filter else {}

                response = await client.get(url, params=params, timeout=10.0)

                if response.status_code == 200:
                    users = response.json()

                    # 为每个User添加 profile Status
                    result = []
                    for user in users:
                        user_data = {
                            "user_id": user["id"],
                            "username": user["username"],
                            "email": user["email"],
                            "role_id": user["role_id"],
                            "role_name": self._get_role_name(user["role_id"]),
                            "has_profile": await self._check_profile_exists(user["id"], user["role_id"]),
                            "created_at": user.get("created_at"),
                        }
                        result.append(user_data)

                    return result
                else:
                    raise HTTPException(
                        status_code=response.status_code, detail="Failed to fetch users from Auth Service"
                    )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Auth Service unavailable: {str(e)}"
            )

    async def get_user_detail(self, user_id: int) -> dict:
        """Get User Details（Contains Profile Information）"""
        try:
            async with httpx.AsyncClient() as client:
                # Call Auth Service GetUser基本Information
                url = f"{settings.AUTH_SERVICE_URL}/admin/users/{user_id}"
                response = await client.get(url, timeout=10.0)

                if response.status_code == 404:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail="Failed to fetch user from Auth Service"
                    )

                user = response.json()

                # GetUser的 Profile
                profile = None
                if user["role_id"] == 1:  # Customer
                    customer_profile = await self.customer_dao.get_by_user_id(user_id)
                    if customer_profile:
                        profile = customer_profile.model_dump(mode="json")
                    else:
                        # Return默认的 Customer Profile 结构
                        profile = {
                            "user_id": user_id,
                            "location": "NORTH",
                            "address": None,
                            "budget_preference": 0.0,
                            "created_at": None,
                            "updated_at": None,
                        }
                elif user["role_id"] == 2:  # Provider
                    provider_profile = await self.provider_dao.get_by_user_id(user_id)
                    if provider_profile:
                        profile = provider_profile.model_dump(mode="json")
                    else:
                        # Return默认的 Provider Profile 结构
                        profile = {
                            "user_id": user_id,
                            "skills": [],
                            "experience_years": 0,
                            "hourly_rate": 0.0,
                            "availability": None,
                            "portfolio": [],
                            "rating": 5.0,
                            "total_reviews": 0,
                            "created_at": None,
                            "updated_at": None,
                        }

                return {
                    "user_id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role_id": user["role_id"],
                    "role_name": self._get_role_name(user["role_id"]),
                    "profile": profile,
                    "created_at": user.get("created_at"),
                }
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Auth Service unavailable: {str(e)}"
            )

    async def update_user(self, user_id: int, update_data: UpdateUserRequest) -> Optional[dict]:
        """Update User InformationAnd Profile"""
        try:
            async with httpx.AsyncClient() as client:
                # 1. Update Auth Service 的UserFields（username, email, role_id）
                auth_fields = {}
                if update_data.username is not None:
                    auth_fields["username"] = update_data.username
                if update_data.email is not None:
                    auth_fields["email"] = update_data.email
                if update_data.role_id is not None:
                    auth_fields["role_id"] = update_data.role_id

                if auth_fields:
                    url = f"{settings.AUTH_SERVICE_URL}/admin/users/{user_id}"
                    response = await client.put(url, json=auth_fields, timeout=10.0)

                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code, detail="Failed to update user in Auth Service"
                        )

                # 2. GetUserCurrentRole，确定Update哪个 Profile
                url = f"{settings.AUTH_SERVICE_URL}/admin/users/{user_id}"
                response = await client.get(url, timeout=10.0)

                if response.status_code == 404:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail="Failed to fetch user from Auth Service"
                    )

                user_info = response.json()
                current_role_id = user_info.get("role_id")

                # 3. ByRoleUpdate对应的 Profile
                if current_role_id == 1:  # Customer
                    # 提取 Customer Profile Fields
                    customer_fields = {}
                    if update_data.location is not None:
                        customer_fields["location"] = update_data.location
                    if update_data.address is not None:
                        customer_fields["address"] = update_data.address
                    if update_data.budget_preference is not None:
                        customer_fields["budget_preference"] = update_data.budget_preference

                    # Update Customer Profile
                    if customer_fields:
                        customer_profile = await self.customer_dao.get_by_user_id(user_id)
                        if customer_profile:
                            await self.customer_dao.update(user_id=user_id, update_data=customer_fields)
                            logger.info(
                                f"已更新 Customer Profile: user_id={user_id}, fields={list(customer_fields.keys())}"
                            )
                        else:
                            logger.warning(f"Customer Profile 不存在: user_id={user_id}")

                elif current_role_id == 2:  # Provider
                    # 提取 Provider Profile Fields
                    provider_fields = {}
                    if update_data.skills is not None:
                        provider_fields["skills"] = update_data.skills
                    if update_data.experience_years is not None:
                        provider_fields["experience_years"] = update_data.experience_years
                    if update_data.hourly_rate is not None:
                        provider_fields["hourly_rate"] = update_data.hourly_rate
                    if update_data.availability is not None:
                        provider_fields["availability"] = update_data.availability
                    if update_data.portfolio is not None:
                        provider_fields["portfolio"] = update_data.portfolio

                    # Update Provider Profile
                    if provider_fields:
                        provider_profile = await self.provider_dao.get_by_user_id(user_id)
                        if provider_profile:
                            await self.provider_dao.update(user_id=user_id, update_data=provider_fields)
                            logger.info(
                                f"已更新 Provider Profile: user_id={user_id}, fields={list(provider_fields.keys())}"
                            )
                        else:
                            logger.warning(f"Provider Profile 不存在: user_id={user_id}")

                # 4. ReturnUpdate后的完整UserInformation
                return await self.get_user_detail(user_id)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新用户失败: user_id={user_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update user: {str(e)}"
            )

    async def delete_user(self, user_id: int) -> bool:
        """Delete User（Including Profile）"""
        try:
            # 1. FirstDelete User的 Profile
            customer_profile = await self.customer_dao.get_by_user_id(user_id)
            if customer_profile:
                await self.customer_dao.delete(user_id)

            provider_profile = await self.provider_dao.get_by_user_id(user_id)
            if provider_profile:
                await self.provider_dao.delete(user_id)

            # 2. Call Auth Service Delete User
            async with httpx.AsyncClient() as client:
                url = f"{settings.AUTH_SERVICE_URL}/admin/users/{user_id}"
                response = await client.delete(url, timeout=10.0)

                if response.status_code == 404:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail="Failed to delete user")

                return True
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Auth Service unavailable: {str(e)}"
            )

    async def _check_profile_exists(self, user_id: int, role_id: int) -> bool:
        """CheckUser是否With Profile"""
        if role_id == 1:  # Customer
            profile = await self.customer_dao.get_by_user_id(user_id)
            return profile is not None
        elif role_id == 2:  # Provider
            profile = await self.provider_dao.get_by_user_id(user_id)
            return profile is not None
        return False

    @staticmethod
    def _get_role_name(role_id: int) -> str:
        """GetRoleName称"""
        role_names = {1: "customer", 2: "provider", 3: "admin"}
        return role_names.get(role_id, "unknown")
