from pydantic import BaseModel
from typing import Optional

class PayOrderRequest(BaseModel):
    """支付订单请求"""
    order_id: int

class PayOrderResponse(BaseModel):
    """支付订单响应（简化版）"""
    payment_id: int
    order_id: int
    amount: float
    message: str

class PaymentDetail(BaseModel):
    """支付详情"""
    id: int
    order_id: int
    customer_id: int
    provider_id: Optional[int]
    amount: float
    payment_method: str
    status: str
    transaction_id: Optional[str]
    created_at: str
    updated_at: str