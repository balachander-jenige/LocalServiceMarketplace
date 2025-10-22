from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, UTC

from ..dao.order_dao import OrderDAO
from ..models.order import Order, OrderStatus, LocationEnum, ServiceType
from ..domain.events.order_created import OrderCreatedEvent
from ..domain.events.order_cancelled import OrderCancelledEvent
from ..events.publishers.event_publisher import EventPublisher

class CustomerOrderService:
    """客户订单服务"""
    
    @staticmethod
    async def publish_order(
        db: AsyncSession,
        customer_id: int,
        title: str,
        description: str,
        service_type: str,
        price: float,
        location: str,
        address: str,
        service_start_time: Optional[datetime] = None,
        service_end_time: Optional[datetime] = None
    ) -> Order:
        """发布订单 - 状态为 pending_review,等待管理员审核"""
        # 创建订单
        order = await OrderDAO.create_order(
            db=db,
            customer_id=customer_id,
            title=title,
            description=description,
            service_type=ServiceType(service_type),
            price=price,
            location=LocationEnum(location),
            address=address,
            service_start_time=service_start_time,
            service_end_time=service_end_time
        )
        
        # 发布订单创建事件
        event = OrderCreatedEvent(
            order_id=order.id,
            customer_id=customer_id,
            title=title,
            price=price,
            location=location,
            timestamp=datetime.now(UTC)
        )
        await EventPublisher.publish_order_created(event)
        
        return order
    
    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        customer_id: int,
        order_id: int
    ) -> Order:
        """取消订单"""
        order = await OrderDAO.get_order_by_id(db, order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # 只有 pending_review, pending 或 accepted 状态可取消
        if order.status not in [OrderStatus.pending_review, OrderStatus.pending, OrderStatus.accepted]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The order cannot be cancelled!"
            )
        
        # 更新订单状态
        updated_order = await OrderDAO.update_order_status(
            db, order_id, OrderStatus.cancelled
        )
        
        # 发布订单取消事件
        event = OrderCancelledEvent(
            order_id=order_id,
            customer_id=customer_id,
            provider_id=order.provider_id,
            timestamp=datetime.now(UTC)
        )
        await EventPublisher.publish_order_cancelled(event)
        
        return updated_order
    
    @staticmethod
    async def get_my_orders(
        db: AsyncSession,
        customer_id: int
    ) -> List[Order]:
        """获取我的订单（进行中）"""
        return await OrderDAO.get_customer_orders(
            db,
            customer_id,
            statuses=[
                OrderStatus.pending_review,
                OrderStatus.pending,
                OrderStatus.accepted,
                OrderStatus.in_progress
            ]
        )
    
    @staticmethod
    async def get_order_detail(
        db: AsyncSession,
        customer_id: int,
        order_id: int
    ) -> Order:
        """获取订单详情"""
        order = await OrderDAO.get_order_by_id(db, order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        return order
    
    @staticmethod
    async def get_order_history(
        db: AsyncSession,
        customer_id: int
    ) -> List[Order]:
        """获取订单历史（所有订单）"""
        return await OrderDAO.get_customer_orders(db, customer_id)