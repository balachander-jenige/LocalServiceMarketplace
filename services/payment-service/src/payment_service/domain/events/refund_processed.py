from datetime import datetime

from pydantic import BaseModel


class RefundProcessedEvent(BaseModel):
    """RefundHandleCompleteEvent"""

    refund_id: int
    order_id: int
    customer_id: int
    amount: float
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
