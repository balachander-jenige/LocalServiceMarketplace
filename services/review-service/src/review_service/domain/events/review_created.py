from datetime import datetime

from pydantic import BaseModel


class ReviewCreatedEvent(BaseModel):
    review_id: str
    order_id: int
    customer_id: int
    provider_id: int
    stars: int
    content: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
