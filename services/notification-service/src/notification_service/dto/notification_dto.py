from typing import List, Optional

from pydantic import BaseModel


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
