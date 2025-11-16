from datetime import datetime

from pydantic import BaseModel


class OrderStatusChangedEvent(BaseModel):
    """Order Status Changed Event"""

    order_id: int
    customer_id: int
    provider_id: int
    old_status: str
    new_status: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
