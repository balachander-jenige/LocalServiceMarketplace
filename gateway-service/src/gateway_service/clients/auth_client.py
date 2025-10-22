from .base_client import BaseClient
from ..core.config import settings
from typing import Dict, Any

class AuthClient(BaseClient):
    def __init__(self):
        super().__init__(settings.AUTH_SERVICE_URL)
    
    async def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """用户注册"""
        return await self._make_request("POST", "/auth/register", json_data=data)
    
    async def login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """用户登录"""
        return await self._make_request("POST", "/auth/login", json_data=data)
    
    async def register_admin(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """管理员注册"""
        return await self._make_request("POST", "/auth/admin/register", json_data=data)
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """获取当前用户信息"""
        return await self._make_request("GET", "/users/me", token=token)

auth_client = AuthClient()