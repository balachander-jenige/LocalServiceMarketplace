from datetime import UTC, datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dao.order_dao import OrderDAO
from ..domain.events.order_approved import OrderApprovedEvent
from ..domain.events.order_rejected import OrderRejectedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..models.order import LocationEnum, Order, OrderStatus, ServiceType


class AdminOrderService:
    """Admin Order Service"""

    @staticmethod
    async def get_all_orders(db: AsyncSession, status_filter: Optional[str] = None) -> List[Order]:
        """Get All Orders（CanByStatusFilter）"""
        if status_filter:
            try:
                status_enum = OrderStatus(status_filter)
                return await OrderDAO.get_orders_by_status(db, status_enum)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {status_filter}")
        return await OrderDAO.get_all_orders(db)

    @staticmethod
    async def get_pending_review_orders(db: AsyncSession) -> List[Order]:
        """GetAll待审核Order"""
        return await OrderDAO.get_orders_by_status(db, OrderStatus.pending_review)

    @staticmethod
    async def approve_order(
        db: AsyncSession, order_id: int, approved: bool, reject_reason: Optional[str] = None
    ) -> Order:
        """审批Order（Approve或Reject）"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.status != OrderStatus.pending_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending_review orders can be approved/rejected"
            )

        if approved:
            # Approve -> Status变为 pending
            updated_order = await OrderDAO.update_order_status(db, order_id, OrderStatus.pending)

            # Publish Order Approved Event
            event = OrderApprovedEvent(order_id=order_id, customer_id=order.customer_id, timestamp=datetime.now(UTC))
            await EventPublisher.publish_order_approved(event)

        else:
            # Reject -> Status变为 cancelled
            if not reject_reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Reject reason is required when rejecting an order"
                )

            updated_order = await OrderDAO.update_order_status(db, order_id, OrderStatus.cancelled)

            # Publish Order Rejected Event
            event = OrderRejectedEvent(
                order_id=order_id,
                customer_id=order.customer_id,
                reject_reason=reject_reason,
                timestamp=datetime.now(UTC),
            )
            await EventPublisher.publish_order_rejected(event)

        return updated_order

    @staticmethod
    async def update_order(
        db: AsyncSession,
        order_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        service_type: Optional[str] = None,
        price: Optional[float] = None,
        location: Optional[str] = None,
        address: Optional[str] = None,
        service_start_time: Optional[datetime] = None,
        service_end_time: Optional[datetime] = None,
        order_status: Optional[str] = None,
    ) -> Order:
        """UpdateOrderInformation（AdminPermission）"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # 构建UpdateData
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if service_type is not None:
            try:
                update_data["service_type"] = ServiceType(service_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid service_type: {service_type}"
                )
        if price is not None:
            if price <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price must be positive")
            update_data["price"] = price
        if location is not None:
            try:
                update_data["location"] = LocationEnum(location)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid location: {location}")
        if address is not None:
            update_data["address"] = address
        if service_start_time is not None:
            update_data["service_start_time"] = service_start_time
        if service_end_time is not None:
            update_data["service_end_time"] = service_end_time
        if order_status is not None:
            try:
                update_data["status"] = OrderStatus(order_status)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {order_status}")

        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update")

        # ExecuteUpdate
        return await OrderDAO.update_order(db, order_id, **update_data)

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: int) -> bool:
        """DeleteOrder（AdminPermission）"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return await OrderDAO.delete_order(db, order_id)

    @staticmethod
    async def get_order_detail(db: AsyncSession, order_id: int) -> Order:
        """Get Order Details（AdminPermission）"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return order
