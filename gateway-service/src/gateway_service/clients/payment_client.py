from typing import Any, Dict

from ..core.config import settings
from .base_client import BaseClient


class PaymentClient(BaseClient):
    def __init__(self):
        super().__init__(settings.PAYMENT_SERVICE_URL)

    async def pay_order(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """客户支付订单（模拟支付）"""
        return await self._make_request("POST", "/customer/payments/pay", token=token, json_data=data)


payment_client = PaymentClient()
