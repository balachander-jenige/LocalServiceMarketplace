from pydantic import BaseModel
from datetime import datetime

class OrderAcceptedEvent(BaseModel):
    """订单被接受事件"""
    order_id: int
    customer_id: int
    provider_id: int
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }