from typing import Any, Dict

from ..core.config import settings
from .base_client import BaseClient


class NotificationClient(BaseClient):
    def __init__(self):
        super().__init__(settings.NOTIFICATION_SERVICE_URL)

    async def get_customer_inbox(self, token: str) -> Dict[str, Any]:
        """获取客户收件箱"""
        return await self._make_request("GET", "/customer/inbox/", token=token)

    async def get_provider_inbox(self, token: str) -> Dict[str, Any]:
        """获取服务商收件箱"""
        return await self._make_request("GET", "/provider/inbox/", token=token)

    async def admin_send_customer_notification(self, user_id: int, message: str, token: str) -> Dict[str, Any]:
        """管理员发送通知给客户"""
        return await self._make_request("POST", f"/admin/notifications/customer/{user_id}", token=token, json_data={"message": message})

    async def admin_send_provider_notification(self, user_id: int, message: str, token: str) -> Dict[str, Any]:
        """管理员发送通知给服务商"""
        return await self._make_request("POST", f"/admin/notifications/provider/{user_id}", token=token, json_data={"message": message})


notification_client = NotificationClient()
