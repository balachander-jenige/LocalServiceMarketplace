from .base_client import BaseClient
from ..core.config import settings
from typing import Dict, Any, List

class OrderClient(BaseClient):
    def __init__(self):
        super().__init__(settings.ORDER_SERVICE_URL)
    
    # Customer endpoints
    async def publish_order(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """客户发布订单"""
        return await self._make_request("POST", "/customer/orders/publish", token=token, json_data=data)
    
    async def get_customer_orders(self, token: str) -> List[Dict[str, Any]]:
        """获取客户订单列表（进行中）"""
        return await self._make_request("GET", "/customer/orders/my", token=token)
    
    async def get_customer_order_history(self, token: str) -> List[Dict[str, Any]]:
        """获取客户订单历史"""
        return await self._make_request("GET", "/customer/orders/history", token=token)
    
    async def cancel_order(self, order_id: int, token: str) -> Dict[str, Any]:
        """客户取消订单"""
        return await self._make_request("POST", f"/customer/orders/cancel/{order_id}", token=token)
    
    # Provider endpoints
    async def get_available_orders(self, token: str) -> List[Dict[str, Any]]:
        """获取可接单列表"""
        return await self._make_request("GET", "/provider/orders/available", token=token)
    
    async def accept_order(self, order_id: int, token: str) -> Dict[str, Any]:
        """服务商接单"""
        return await self._make_request("POST", f"/provider/orders/accept/{order_id}", token=token)
    
    async def update_order_status(self, order_id: int, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新订单状态"""
        return await self._make_request("POST", f"/provider/orders/status/{order_id}", token=token, json_data=data)
    
    async def get_provider_order_history(self, token: str) -> List[Dict[str, Any]]:
        """获取服务商订单历史"""
        return await self._make_request("GET", "/provider/orders/history", token=token)

order_client = OrderClient()