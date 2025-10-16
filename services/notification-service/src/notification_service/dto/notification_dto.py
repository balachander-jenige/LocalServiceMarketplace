from pydantic import BaseModel
from typing import Optional, List

class NotificationItem(BaseModel):
    customer_id: Optional[int] = None
    provider_id: Optional[int] = None
    order_id: Optional[int] = None
    message: str
    created_at: str
    is_read: bool

class NotificationListResponse(BaseModel):
    items: List[NotificationItem]
    total: int