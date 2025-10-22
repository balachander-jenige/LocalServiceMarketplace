from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerInbox(BaseModel):
    customer_id: int = Field(...)
    order_id: Optional[int] = None
    message: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "order_id": 123,
                "message": "Your order has been accepted.",
                "created_at": "2025-10-16T12:00:00Z",
                "is_read": False
            }
        }