from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class ProfileUpdatedEvent(BaseModel):
    """UserProfileUpdateEvent"""

    user_id: int
    profile_type: str  # "customer" or "provider"
    updated_fields: Dict[str, Any]
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
