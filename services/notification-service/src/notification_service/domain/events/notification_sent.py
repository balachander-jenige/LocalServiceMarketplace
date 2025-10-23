from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationSentEvent(BaseModel):
    recipient_id: int
    recipient_type: str  # "customer" or "provider"
    order_id: Optional[int]
    message: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
