from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class RechargeRequest(BaseModel):
    """充值请求"""
    amount: float
    
    @validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("充值金额必须大于0 / Recharge amount must be greater than 0")
        return v

class RechargeResponse(BaseModel):
    """充值响应"""
    transaction_id: int
    balance: float
    message: str

class PayOrderRequest(BaseModel):
    """支付订单请求"""
    order_id: int

class PayOrderResponse(BaseModel):
    """支付订单响应"""
    payment_id: int
    order_id: int
    balance: float
    message: str

class PaymentDetail(BaseModel):
    """支付详情"""
    id: int
    order_id: int
    customer_id: int
    provider_id: Optional[int]
    amount: float
    payment_method: str
    status: str
    transaction_id: Optional[str]
    created_at: str
    updated_at: str