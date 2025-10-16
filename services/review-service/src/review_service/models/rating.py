from pydantic import BaseModel, Field

class ProviderRating(BaseModel):
    provider_id: int = Field(...)
    average_rating: float = Field(default=5.0)
    total_reviews: int = Field(default=0)