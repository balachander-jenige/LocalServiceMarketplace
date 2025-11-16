from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一 API 响应Format"""

    success: bool
    data: Optional[Any] = None
    message: str = "Success"
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error响应Format"""

    detail: str
