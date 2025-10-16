from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..dto.order_dto import OrderSummary, OrderDetail, AcceptOrderResponse
from ..dto.order_status_dto import UpdateStatusRequest, UpdateStatusResponse
from ..services.provider_order_service import ProviderOrderService

router = APIRouter(prefix="/provider/orders", tags=["Provider Orders"])

@router.get("/available", response_model=List[OrderSummary])
async def browse_available_orders(
    location: Optional[str] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    keyword: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """浏览可用订单"""
    orders = await ProviderOrderService.list_available_orders(
        db=db,
        location=location,
        min_price=min_price,
        max_price=max_price,
        keyword=keyword
    )
    
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

@router.post("/accept/{order_id}", response_model=AcceptOrderResponse)
async def accept_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """接受订单"""
    order = await ProviderOrderService.accept_order(db, user_id, order_id)
    
    return AcceptOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"You have successfully accepted the order: {order.id}."
    )

@router.post("/status/{order_id}", response_model=UpdateStatusResponse)
async def update_order_status(
    order_id: int,
    data: UpdateStatusRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新订单状态"""
    order = await ProviderOrderService.update_order_status(
        db, user_id, order_id, data.new_status
    )
    
    return UpdateStatusResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"Order {order.id} status updated to {order.status.value}."
    )

@router.get("/history", response_model=List[OrderSummary])
async def get_order_history(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取订单历史"""
    orders = await ProviderOrderService.get_order_history(db, user_id)
    
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
    order = await ProviderOrderService.get_order_detail(db, user_id, order_id)
    
    return OrderDetail(
        id=order.id,
        customer_id=order.customer_id,
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