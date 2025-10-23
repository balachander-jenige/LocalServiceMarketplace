from .base_client import BaseClient
from ..core.config import settings
from typing import Dict, Any

class NotificationClient(BaseClient):
    def __init__(self):
        super().__init__(settings.NOTIFICATION_SERVICE_URL)
    
    async def get_customer_inbox(self, token: str) -> Dict[str, Any]:
        """获取客户收件箱"""
        return await self._make_request("GET", "/customer/inbox/", token=token)
    
    async def get_provider_inbox(self, token: str) -> Dict[str, Any]:
        """获取服务商收件箱"""
        return await self._make_request("GET", "/provider/inbox/", token=token)

notification_client = NotificationClient()