from pydantic import BaseModel
from datetime import datetime

class OrderCreatedEvent(BaseModel):
    """订单创建事件"""
    order_id: int
    customer_id: int
    title: str
    price: float
    location: str
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }