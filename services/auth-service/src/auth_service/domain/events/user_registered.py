from datetime import datetime

from pydantic import BaseModel


class UserRegisteredEvent(BaseModel):
    """User Registered Event"""

    user_id: int
    username: str
    email: str
    role_id: int
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
