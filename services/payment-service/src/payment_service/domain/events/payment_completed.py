from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentCompletedEvent(BaseModel):
    """支付完成事件"""
    payment_id: int
    order_id: int
    customer_id: int
    provider_id: Optional[int]
    amount: float
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }