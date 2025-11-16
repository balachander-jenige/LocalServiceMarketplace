from typing import Any, Dict, Optional

from ..core.config import settings
from .base_client import BaseClient


class UserClient(BaseClient):
    def __init__(self):
        super().__init__(settings.USER_SERVICE_URL)

    async def get_customer_profile(self, token: str) -> Dict[str, Any]:
        """GetCustomerProfile"""
        return await self._make_request("GET", "/customer/profile/me", token=token)

    async def get_provider_profile(self, token: str) -> Dict[str, Any]:
        """GetProviderProfile"""
        return await self._make_request("GET", "/provider/profile/me", token=token)

    async def update_customer_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """UpdateCustomerProfile"""
        return await self._make_request("PUT", "/customer/profile/me", token=token, json_data=data)

    async def update_provider_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """UpdateProviderProfile"""
        return await self._make_request("PUT", "/provider/profile/me", token=token, json_data=data)

    async def create_customer_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """CreateCustomerProfile"""
        return await self._make_request("POST", "/customer/profile/", token=token, json_data=data)

    async def create_provider_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """CreateProviderProfile"""
        return await self._make_request("POST", "/provider/profile/", token=token, json_data=data)

    async def get_user_by_id(self, user_id: int, token: str) -> Dict[str, Any]:
        """ByIDGet User Information"""
        return await self._make_request("GET", f"/users/{user_id}", token=token)

    # ==================== Admin User Management ====================
    async def get_all_users(self, token: str, role_id: Optional[int] = None) -> Dict[str, Any]:
        """AdminGetAllUser（CanByRoleFilter）"""
        params = {"role_id": role_id} if role_id else {}
        return await self._make_request("GET", "/admin/users", token=token, params=params)

    async def get_user_detail_admin(self, user_id: int, token: str) -> Dict[str, Any]:
        """AdminGet User Details"""
        return await self._make_request("GET", f"/admin/users/{user_id}", token=token)

    async def update_user_admin(self, user_id: int, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """AdminUpdate User Information"""
        return await self._make_request("PUT", f"/admin/users/{user_id}", token=token, json_data=data)

    async def delete_user_admin(self, user_id: int, token: str) -> Dict[str, Any]:
        """AdminDelete User"""
        return await self._make_request("DELETE", f"/admin/users/{user_id}", token=token)


user_client = UserClient()
