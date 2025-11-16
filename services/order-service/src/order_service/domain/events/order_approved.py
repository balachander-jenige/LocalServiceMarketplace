from datetime import datetime

from pydantic import BaseModel


class OrderApprovedEvent(BaseModel):
    """Order审批通过Event"""

    order_id: int
    customer_id: int
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
