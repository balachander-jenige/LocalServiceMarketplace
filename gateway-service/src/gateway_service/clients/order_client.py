from typing import Any, Dict, List

from ..core.config import settings
from .base_client import BaseClient


class OrderClient(BaseClient):
    def __init__(self):
        super().__init__(settings.ORDER_SERVICE_URL)

    # Customer endpoints
    async def publish_order(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """CustomerPublishOrder"""
        return await self._make_request("POST", "/customer/orders/publish", token=token, json_data=data)

    async def get_customer_orders(self, token: str) -> List[Dict[str, Any]]:
        """GetCustomerOrderList（进行中）"""
        return await self._make_request("GET", "/customer/orders/my", token=token)

    async def get_customer_order_detail(self, order_id: int, token: str) -> Dict[str, Any]:
        """GetCustomerOrderDetails"""
        return await self._make_request("GET", f"/customer/orders/my/{order_id}", token=token)

    async def get_customer_order_history(self, token: str) -> List[Dict[str, Any]]:
        """GetCustomerOrder历史"""
        return await self._make_request("GET", "/customer/orders/history", token=token)

    async def cancel_order(self, order_id: int, token: str) -> Dict[str, Any]:
        """CustomerCancel Order"""
        return await self._make_request("POST", f"/customer/orders/cancel/{order_id}", token=token)

    # Provider endpoints
    async def get_available_orders(
        self,
        token: str,
        location: str = None,
        service_type: str = None,
        min_price: float = None,
        max_price: float = None,
        keyword: str = None,
    ) -> List[Dict[str, Any]]:
        """GetCan接单List - 支持By地点、Service类型、价格范围And关键词筛选"""
        params = {}
        if location:
            params["location"] = location
        if service_type:
            params["service_type"] = service_type
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if keyword:
            params["keyword"] = keyword

        return await self._make_request("GET", "/provider/orders/available", token=token, params=params)

    async def get_available_order_detail(self, order_id: int, token: str) -> Dict[str, Any]:
        """GetCan接单Order的Details"""
        return await self._make_request("GET", f"/provider/orders/available/{order_id}", token=token)

    async def accept_order(self, order_id: int, token: str) -> Dict[str, Any]:
        """Provider接单"""
        return await self._make_request("POST", f"/provider/orders/accept/{order_id}", token=token)

    async def update_order_status(self, order_id: int, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update Order Status"""
        return await self._make_request("POST", f"/provider/orders/status/{order_id}", token=token, json_data=data)

    async def get_provider_order_detail(self, order_id: int, token: str) -> Dict[str, Any]:
        """GetProviderOrderDetails"""
        return await self._make_request("GET", f"/provider/orders/my/{order_id}", token=token)

    async def get_provider_order_history(self, token: str) -> List[Dict[str, Any]]:
        """GetProviderOrder历史"""
        return await self._make_request("GET", "/provider/orders/history", token=token)

    # Admin endpoints
    async def get_all_orders(self, token: str, status: str = None) -> List[Dict[str, Any]]:
        """AdminGet All Orders"""
        params = {"status": status} if status else {}
        return await self._make_request("GET", "/admin/orders", token=token, params=params)

    async def get_pending_review_orders(self, token: str) -> List[Dict[str, Any]]:
        """AdminGet待审核Order"""
        return await self._make_request("GET", "/admin/orders/pending-review", token=token)

    async def get_order_detail_admin(self, order_id: int, token: str) -> Dict[str, Any]:
        """AdminGet Order Details"""
        return await self._make_request("GET", f"/admin/orders/{order_id}", token=token)

    async def approve_order(self, order_id: int, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Admin审批Order"""
        return await self._make_request("POST", f"/admin/orders/{order_id}/approve", token=token, json_data=data)

    async def update_order_admin(self, order_id: int, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """AdminUpdateOrder"""
        return await self._make_request("PUT", f"/admin/orders/{order_id}", token=token, json_data=data)

    async def delete_order_admin(self, order_id: int, token: str) -> Dict[str, Any]:
        """AdminDeleteOrder"""
        return await self._make_request("DELETE", f"/admin/orders/{order_id}", token=token)


order_client = OrderClient()
