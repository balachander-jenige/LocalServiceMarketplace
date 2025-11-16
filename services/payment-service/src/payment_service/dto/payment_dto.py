from typing import Optional

from pydantic import BaseModel


class PayOrderRequest(BaseModel):
    """PaymentOrder请求"""

    order_id: int


class PayOrderResponse(BaseModel):
    """PaymentOrder响应（简化版）"""

    payment_id: int
    order_id: int
    amount: float
    message: str


class PaymentDetail(BaseModel):
    """PaymentDetails"""

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
