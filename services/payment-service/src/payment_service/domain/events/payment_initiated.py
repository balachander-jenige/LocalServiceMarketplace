from datetime import datetime

from pydantic import BaseModel


class PaymentInitiatedEvent(BaseModel):
    """支付发起事件"""

    payment_id: int
    order_id: int
    customer_id: int
    amount: float
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
