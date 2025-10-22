from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..services.admin_order_service import AdminOrderService
from ..dto.order_dto import (
    ApproveOrderRequest,
    ApproveOrderResponse,
    UpdateOrderRequest,
    DeleteOrderResponse,
    OrderSummary,
    OrderDetail
)

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


@router.get("", response_model=List[OrderDetail])
async def get_all_orders(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取所有订单（管理员）"""
    # 注意: 这里需要在网关层验证管理员权限
    orders = await AdminOrderService.get_all_orders(db, status)
    
    return [
        OrderDetail(
            id=order.id,
            customer_id=order.customer_id,
            title=order.title,
            description=order.description,
            service_type=order.service_type.value,
            status=order.status.value,
            price=float(order.price),
            location=order.location.value,
            address=order.address,
            service_start_time=order.service_start_time.isoformat() if order.service_start_time else None,
            service_end_time=order.service_end_time.isoformat() if order.service_end_time else None,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat(),
            provider_id=order.provider_id,
            payment_status=order.payment_status.value
        )
        for order in orders
    ]


@router.get("/pending-review", response_model=List[OrderDetail])
async def get_pending_review_orders(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取待审核订单列表（管理员）"""
    orders = await AdminOrderService.get_pending_review_orders(db)
    
    return [
        OrderDetail(
            id=order.id,
            customer_id=order.customer_id,
            title=order.title,
            description=order.description,
            service_type=order.service_type.value,
            status=order.status.value,
            price=float(order.price),
            location=order.location.value,
            address=order.address,
            service_start_time=order.service_start_time.isoformat() if order.service_start_time else None,
            service_end_time=order.service_end_time.isoformat() if order.service_end_time else None,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat(),
            provider_id=order.provider_id,
            payment_status=order.payment_status.value
        )
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取订单详情（管理员）"""
    order = await AdminOrderService.get_order_detail(db, order_id)
    
    return OrderDetail(
        id=order.id,
        customer_id=order.customer_id,
        title=order.title,
        description=order.description,
        service_type=order.service_type.value,
        status=order.status.value,
        price=float(order.price),
        location=order.location.value,
        address=order.address,
        service_start_time=order.service_start_time.isoformat() if order.service_start_time else None,
        service_end_time=order.service_end_time.isoformat() if order.service_end_time else None,
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
        provider_id=order.provider_id,
        payment_status=order.payment_status.value
    )


@router.post("/{order_id}/approve", response_model=ApproveOrderResponse)
async def approve_order(
    order_id: int,
    request: ApproveOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """审批订单（管理员）"""
    order = await AdminOrderService.approve_order(
        db,
        order_id,
        request.approved,
        request.reject_reason
    )
    
    if request.approved:
        message = "Order approved successfully"
    else:
        message = f"Order rejected: {request.reject_reason}"
    
    return ApproveOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=message
    )


@router.put("/{order_id}", response_model=OrderDetail)
async def update_order(
    order_id: int,
    request: UpdateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新订单信息（管理员）"""
    order = await AdminOrderService.update_order(
        db,
        order_id,
        title=request.title,
        description=request.description,
        service_type=request.service_type,
        price=request.price,
        location=request.location,
        address=request.address,
        service_start_time=request.service_start_time,
        service_end_time=request.service_end_time,
        order_status=request.status
    )
    
    return OrderDetail(
        id=order.id,
        customer_id=order.customer_id,
        title=order.title,
        description=order.description,
        service_type=order.service_type.value,
        status=order.status.value,
        price=float(order.price),
        location=order.location.value,
        address=order.address,
        service_start_time=order.service_start_time.isoformat() if order.service_start_time else None,
        service_end_time=order.service_end_time.isoformat() if order.service_end_time else None,
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
        provider_id=order.provider_id,
        payment_status=order.payment_status.value
    )


@router.delete("/{order_id}", response_model=DeleteOrderResponse)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除订单（管理员）"""
    success = await AdminOrderService.delete_order(db, order_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return DeleteOrderResponse(
        order_id=order_id,
        message="Order deleted successfully"
    )
