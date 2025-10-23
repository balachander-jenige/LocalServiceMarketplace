from pydantic import BaseModel
from datetime import datetime

class OrderRejectedEvent(BaseModel):
    """订单审批拒绝事件"""
    order_id: int
    customer_id: int
    reject_reason: str
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
