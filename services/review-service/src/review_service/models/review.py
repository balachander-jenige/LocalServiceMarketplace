from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Review(BaseModel):
    order_id: int = Field(...)
    customer_id: int = Field(...)
    provider_id: int = Field(...)
    stars: int = Field(..., ge=1, le=5)
    content: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 123,
                "customer_id": 1,
                "provider_id": 2,
                "stars": 5,
                "content": "Great job!",
                "created_at": "2025-10-16T12:00:00Z"
            }
        }