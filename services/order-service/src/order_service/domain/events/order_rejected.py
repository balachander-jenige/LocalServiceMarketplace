from datetime import datetime

from pydantic import BaseModel


class OrderRejectedEvent(BaseModel):
    """Order审批RejectEvent"""

    order_id: int
    customer_id: int
    reject_reason: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
