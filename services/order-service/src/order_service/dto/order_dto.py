from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class PublishOrderRequest(BaseModel):
    """发布订单请求"""
    title: str
    description: Optional[str] = None
    price: float
    location: str
    address: Optional[str] = None

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
    status: str
    price: float
    location: str
    created_at: str

class OrderDetail(BaseModel):
    """订单详情"""
    id: int
    title: str
    description: Optional[str]
    status: str
    price: float
    location: str
    address: Optional[str]
    created_at: str
    updated_at: str
    provider_id: Optional[int]
    payment_status: str

class AcceptOrderResponse(BaseModel):
    """接受订单响应"""
    order_id: int
    status: str
    message: str