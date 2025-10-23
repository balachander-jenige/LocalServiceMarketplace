from datetime import datetime

from pydantic import BaseModel


class RatingUpdatedEvent(BaseModel):
    provider_id: int
    average_rating: float
    total_reviews: int
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
