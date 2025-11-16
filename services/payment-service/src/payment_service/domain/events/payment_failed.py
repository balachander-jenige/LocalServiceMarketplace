from datetime import datetime

from pydantic import BaseModel


class PaymentFailedEvent(BaseModel):
    """Payment Failed Event"""

    payment_id: int
    order_id: int
    customer_id: int
    reason: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
