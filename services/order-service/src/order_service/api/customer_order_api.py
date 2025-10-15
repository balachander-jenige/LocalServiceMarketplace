from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..dto.order_dto import (
    PublishOrderRequest,
    PublishOrderResponse,
    CancelOrderResponse,
    OrderSummary,
    OrderDetail
)
from ..services.customer_order_service import CustomerOrderService

router = APIRouter(prefix="/customer/orders", tags=["Customer Orders"])

@router.post("/publish", response_model=PublishOrderResponse, status_code=status.HTTP_201_CREATED)
async def publish_order(
    data: PublishOrderRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """发布订单"""
    order = await CustomerOrderService.publish_order(
        db=db,
        customer_id=user_id,
        title=data.title,
        description=data.description,
        price=data.price,
        location=data.location,
        address=data.address
    )
    
    return PublishOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"You have successfully published the order: {order.id}."
    )

@router.post("/cancel/{order_id}", response_model=CancelOrderResponse)
async def cancel_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """取消订单"""
    order = await CustomerOrderService.cancel_order(db, user_id, order_id)
    
    return CancelOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"You have successfully cancelled the order: {order.id}."
    )

@router.get("/my", response_model=List[OrderSummary])
async def get_my_orders(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取我的订单（进行中）"""
    orders = await CustomerOrderService.get_my_orders(db, user_id)
    
    return [
        OrderSummary(
            id=o.id,
            title=o.title,
            status=o.status.value,
            price=float(o.price),
            location=o.location.value,
            created_at=str(o.created_at)
        )
        for o in orders
    ]

@router.get("/my/{order_id}", response_model=OrderDetail)
async def get_order_detail(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    order = await CustomerOrderService.get_order_detail(db, user_id, order_id)
    
    return OrderDetail(
        id=order.id,
        title=order.title,
        description=order.description,
        status=order.status.value,
        price=float(order.price),
        location=order.location.value,
        address=order.address,
        created_at=str(order.created_at),
        updated_at=str(order.updated_at),
        provider_id=order.provider_id,
        payment_status=order.payment_status.value
    )

@router.get("/history", response_model=List[OrderSummary])
async def get_order_history(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取订单历史"""
    orders = await CustomerOrderService.get_order_history(db, user_id)
    
    return [
        OrderSummary(
            id=o.id,
            title=o.title,
            status=o.status.value,
            price=float(o.price),
            location=o.location.value,
            created_at=str(o.created_at)
        )
        for o in orders
    ]