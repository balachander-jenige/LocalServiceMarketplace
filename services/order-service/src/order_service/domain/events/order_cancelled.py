from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderCancelledEvent(BaseModel):
    """订单取消事件"""
    order_id: int
    customer_id: int
    provider_id: Optional[int]
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }