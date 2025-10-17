from .base_client import BaseClient
from ..core.config import settings
from typing import Dict, Any

class PaymentClient(BaseClient):
    def __init__(self):
        super().__init__(settings.PAYMENT_SERVICE_URL)
    
    async def recharge_balance(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """客户充值"""
        return await self._make_request("POST", "/customer/payments/recharge", token=token, json_data=data)
    
    async def pay_order(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """客户支付订单"""
        return await self._make_request("POST", "/customer/payments/pay", token=token, json_data=data)

payment_client = PaymentClient()