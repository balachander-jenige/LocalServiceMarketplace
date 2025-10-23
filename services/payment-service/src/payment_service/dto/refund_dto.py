from typing import Optional

from pydantic import BaseModel


class RefundRequest(BaseModel):
    """退款请求"""

    order_id: int
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    """退款响应"""

    refund_id: int
    order_id: int
    amount: float
    status: str
    message: str
