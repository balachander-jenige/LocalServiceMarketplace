from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaymentCompletedEvent(BaseModel):
    """Payment Completed Event"""

    payment_id: int
    order_id: int
    customer_id: int
    provider_id: Optional[int]
    amount: float
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
