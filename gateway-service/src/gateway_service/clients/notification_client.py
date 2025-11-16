from typing import Any, Dict

from ..core.config import settings
from .base_client import BaseClient


class NotificationClient(BaseClient):
    def __init__(self):
        super().__init__(settings.NOTIFICATION_SERVICE_URL)

    async def get_customer_inbox(self, token: str) -> Dict[str, Any]:
        """GetCustomerInbox"""
        return await self._make_request("GET", "/customer/inbox/", token=token)

    async def get_provider_inbox(self, token: str) -> Dict[str, Any]:
        """GetProviderInbox"""
        return await self._make_request("GET", "/provider/inbox/", token=token)

    async def admin_send_customer_notification(self, user_id: int, message: str, token: str) -> Dict[str, Any]:
        """Admin发送Notification给Customer"""
        return await self._make_request("POST", f"/admin/notifications/customer/{user_id}", token=token, json_data={"message": message})

    async def admin_send_provider_notification(self, user_id: int, message: str, token: str) -> Dict[str, Any]:
        """Admin发送Notification给Provider"""
        return await self._make_request("POST", f"/admin/notifications/provider/{user_id}", token=token, json_data={"message": message})


notification_client = NotificationClient()
