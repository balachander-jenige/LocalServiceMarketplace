from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class PublishOrderRequest(BaseModel):
    """发布订单请求"""
    title: str
    description: Optional[str] = None
    service_type: str  # 新增:服务类型
    price: float
    location: str
    address: Optional[str] = None
    service_start_time: Optional[datetime] = None  # 新增:服务开始时间
    service_end_time: Optional[datetime] = None  # 新增:服务结束时间

    @validator("title")
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
    
    @validator("service_type")
    def validate_service_type(cls, v):
        valid_types = ["cleaning_repair", "it_technology", "education_training", 
                      "life_health", "design_consulting", "other"]
        if v not in valid_types:
            raise ValueError(f"Invalid service_type. Must be one of: {', '.join(valid_types)}")
        return v
    
    @validator("service_end_time")
    def validate_service_time(cls, v, values):
        if v and "service_start_time" in values and values["service_start_time"]:
            if v <= values["service_start_time"]:
                raise ValueError("service_end_time must be after service_start_time")
        return v

class PublishOrderResponse(BaseModel):
    """发布订单响应"""
    order_id: int
    status: str
    message: str

class CancelOrderResponse(BaseModel):
    """取消订单响应"""
    order_id: int
    status: str
    message: str

class OrderSummary(BaseModel):
    """订单摘要"""
    id: int
    title: str
    service_type: str  # 新增:服务类型
    status: str
    price: float
    location: str
    created_at: str

class OrderDetail(BaseModel):
    """订单详情"""
    id: int
    customer_id: int
    title: str
    description: Optional[str]
    service_type: str  # 新增:服务类型
    status: str
    price: float
    location: str
    address: Optional[str]
    service_start_time: Optional[str] = None  # 新增:服务开始时间
    service_end_time: Optional[str] = None  # 新增:服务结束时间
    created_at: str
    updated_at: str
    provider_id: Optional[int]
    payment_status: str

class AcceptOrderResponse(BaseModel):
    """接受订单响应"""
    order_id: int
    status: str
    message: str

class ApproveOrderRequest(BaseModel):
    """管理员审批订单请求"""
    approved: bool  # True=批准, False=拒绝
    reject_reason: Optional[str] = None  # 拒绝原因(拒绝时必填)

class ApproveOrderResponse(BaseModel):
    """管理员审批订单响应"""
    order_id: int
    status: str
    message: str

class UpdateOrderRequest(BaseModel):
    """管理员更新订单请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    service_type: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    address: Optional[str] = None
    service_start_time: Optional[datetime] = None
    service_end_time: Optional[datetime] = None
    status: Optional[str] = None

class DeleteOrderResponse(BaseModel):
    """管理员删除订单响应"""
    order_id: int
    message: str