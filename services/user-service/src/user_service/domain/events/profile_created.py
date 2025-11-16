from datetime import datetime

from pydantic import BaseModel


class ProfileCreatedEvent(BaseModel):
    """UserProfileCreateEvent"""

    user_id: int
    profile_type: str  # "customer" or "provider"
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
