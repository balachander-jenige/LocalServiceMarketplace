from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderCancelledEvent(BaseModel):
    """Order Cancelled Event"""

    order_id: int
    customer_id: int
    provider_id: Optional[int]
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
