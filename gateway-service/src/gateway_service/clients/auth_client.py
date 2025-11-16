from typing import Any, Dict

from ..core.config import settings
from .base_client import BaseClient


class AuthClient(BaseClient):
    def __init__(self):
        super().__init__(settings.AUTH_SERVICE_URL)

    async def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """User Registration"""
        return await self._make_request("POST", "/auth/register", json_data=data)

    async def login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """User Login"""
        return await self._make_request("POST", "/auth/login", json_data=data)

    async def register_admin(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """AdminRegistration"""
        return await self._make_request("POST", "/auth/admin/register", json_data=data)

    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get Current UserInformation"""
        return await self._make_request("GET", "/users/me", token=token)


auth_client = AuthClient()
