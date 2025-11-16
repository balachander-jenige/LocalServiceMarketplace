from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CustomerProfileCreate(BaseModel):
    """CreateCustomerProfile请求"""

    location: str = "NORTH"
    address: Optional[str] = None
    budget_preference: float = 0.0


class CustomerProfileUpdate(BaseModel):
    """UpdateCustomerProfile请求"""

    location: Optional[str] = None
    address: Optional[str] = None
    budget_preference: Optional[float] = None
    # balance Field Removed - Phase 3 Modification


class CustomerProfileResponse(BaseModel):
    """CustomerProfile响应"""

    user_id: int
    location: str
    address: Optional[str]
    budget_preference: float
    # balance Field Removed - Phase 3 Modification
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
