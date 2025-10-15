from pydantic import BaseModel
from datetime import datetime

class OrderStatusChangedEvent(BaseModel):
    """订单状态变更事件"""
    order_id: int
    customer_id: int
    provider_id: int
    old_status: str
    new_status: str
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }