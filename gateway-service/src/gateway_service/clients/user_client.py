from .base_client import BaseClient
from ..core.config import settings
from typing import Dict, Any, Optional

class UserClient(BaseClient):
    def __init__(self):
        super().__init__(settings.USER_SERVICE_URL)
    
    async def get_customer_profile(self, token: str) -> Dict[str, Any]:
        """获取客户资料"""
        return await self._make_request("GET", "/customer/profile/me", token=token)
    
    async def get_provider_profile(self, token: str) -> Dict[str, Any]:
        """获取服务商资料"""
        return await self._make_request("GET", "/provider/profile/me", token=token)
    
    async def update_customer_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新客户资料"""
        return await self._make_request("PUT", "/customer/profile/me", token=token, json_data=data)
    
    async def update_provider_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新服务商资料"""
        return await self._make_request("PUT", "/provider/profile/me", token=token, json_data=data)
    
    async def create_customer_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建客户资料"""
        return await self._make_request("POST", "/customer/profile/", token=token, json_data=data)
    
    async def create_provider_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建服务商资料"""
        return await self._make_request("POST", "/provider/profile/", token=token, json_data=data)
    
    async def get_user_by_id(self, user_id: int, token: str) -> Dict[str, Any]:
        """根据ID获取用户信息"""
        return await self._make_request("GET", f"/users/{user_id}", token=token)
    
    # ==================== Admin User Management ====================
    async def get_all_users(self, token: str, role_id: Optional[int] = None) -> Dict[str, Any]:
        """管理员获取所有用户（可按角色过滤）"""
        params = {"role_id": role_id} if role_id else {}
        return await self._make_request("GET", "/admin/users", token=token, params=params)
    
    async def get_user_detail_admin(self, user_id: int, token: str) -> Dict[str, Any]:
        """管理员获取用户详情"""
        return await self._make_request("GET", f"/admin/users/{user_id}", token=token)
    
    async def update_user_admin(self, user_id: int, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """管理员更新用户信息"""
        return await self._make_request("PUT", f"/admin/users/{user_id}", token=token, json_data=data)
    
    async def delete_user_admin(self, user_id: int, token: str) -> Dict[str, Any]:
        """管理员删除用户"""
        return await self._make_request("DELETE", f"/admin/users/{user_id}", token=token)

user_client = UserClient()