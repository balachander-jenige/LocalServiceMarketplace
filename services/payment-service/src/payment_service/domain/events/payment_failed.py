from datetime import datetime

from pydantic import BaseModel


class PaymentFailedEvent(BaseModel):
    """支付失败事件"""

    payment_id: int
    order_id: int
    customer_id: int
    reason: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
