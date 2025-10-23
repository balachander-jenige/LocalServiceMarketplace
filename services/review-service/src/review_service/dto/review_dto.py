from typing import Optional

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    order_id: int
    stars: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    content: Optional[str] = Field(None, description="Review content")


class CreateReviewResponse(BaseModel):
    review_id: Optional[str]
    order_id: int
    stars: int
    content: Optional[str]
    message: str


class ProviderRatingResponse(BaseModel):
    provider_id: int
    average_rating: float
    total_reviews: int
