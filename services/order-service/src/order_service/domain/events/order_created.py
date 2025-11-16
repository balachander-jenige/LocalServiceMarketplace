from datetime import datetime

from pydantic import BaseModel


class OrderCreatedEvent(BaseModel):
    """Order Created Event"""

    order_id: int
    customer_id: int
    title: str
    price: float
    location: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
