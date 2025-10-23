from datetime import datetime

from pydantic import BaseModel


class OrderAcceptedEvent(BaseModel):
    """订单被接受事件"""

    order_id: int
    customer_id: int
    provider_id: int
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
