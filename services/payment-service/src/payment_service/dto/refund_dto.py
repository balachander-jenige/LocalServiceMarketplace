from typing import Optional

from pydantic import BaseModel


class RefundRequest(BaseModel):
    """Refund请求"""

    order_id: int
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    """Refund响应"""

    refund_id: int
    order_id: int
    amount: float
    status: str
    message: str
