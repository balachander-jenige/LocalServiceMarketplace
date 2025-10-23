from pydantic import BaseModel


class UpdateStatusRequest(BaseModel):
    """更新订单状态请求"""

    new_status: str  # "in_progress" or "completed"


class UpdateStatusResponse(BaseModel):
    """更新订单状态响应"""

    order_id: int
    status: str
    message: str
