from pydantic import BaseModel


class UpdateStatusRequest(BaseModel):
    """Update Order Status请求"""

    new_status: str  # "in_progress" or "completed"


class UpdateStatusResponse(BaseModel):
    """Update Order Status响应"""

    order_id: int
    status: str
    message: str
