from datetime import UTC, datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dao.order_dao import OrderDAO
from ..domain.events.order_cancelled import OrderCancelledEvent
from ..domain.events.order_created import OrderCreatedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..models.order import LocationEnum, Order, OrderStatus, ServiceType


class CustomerOrderService:
    """Customer Order Service"""

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
        service_end_time: Optional[datetime] = None,
    ) -> Order:
        """PublishOrder - Status为 pending_review,等待Admin审核"""
        # Create Order
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
            service_end_time=service_end_time,
        )

        # Publish Order Created Event
        event = OrderCreatedEvent(
            order_id=order.id,
            customer_id=customer_id,
            title=title,
            price=price,
            location=location,
            timestamp=datetime.now(UTC),
        )
        await EventPublisher.publish_order_created(event)

        return order

    @staticmethod
    async def cancel_order(db: AsyncSession, customer_id: int, order_id: int) -> Order:
        """Cancel Order"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.customer_id != customer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

        # OnlyWith pending_review, pending 或 accepted StatusCanCancel
        if order.status not in [OrderStatus.pending_review, OrderStatus.pending, OrderStatus.accepted]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The order cannot be cancelled!")

        # Update Order Status
        updated_order = await OrderDAO.update_order_status(db, order_id, OrderStatus.cancelled)

        # Publish Order Cancelled Event
        event = OrderCancelledEvent(
            order_id=order_id, customer_id=customer_id, provider_id=order.provider_id, timestamp=datetime.now(UTC)
        )
        await EventPublisher.publish_order_cancelled(event)

        return updated_order

    @staticmethod
    async def get_my_orders(db: AsyncSession, customer_id: int) -> List[Order]:
        """Get我的Order（进行中）"""
        return await OrderDAO.get_customer_orders(
            db,
            customer_id,
            statuses=[OrderStatus.pending_review, OrderStatus.pending, OrderStatus.accepted, OrderStatus.in_progress],
        )

    @staticmethod
    async def get_order_detail(db: AsyncSession, customer_id: int, order_id: int) -> Order:
        """Get Order Details"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.customer_id != customer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

        return order

    @staticmethod
    async def get_order_history(db: AsyncSession, customer_id: int) -> List[Order]:
        """GetOrder历史（AllOrder）"""
        return await OrderDAO.get_customer_orders(db, customer_id)
