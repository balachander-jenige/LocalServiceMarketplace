from datetime import datetime

from pydantic import BaseModel


class OrderApprovedEvent(BaseModel):
    """订单审批通过事件"""

    order_id: int
    customer_id: int
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
