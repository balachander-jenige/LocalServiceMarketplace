from datetime import UTC, datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dao.order_dao import OrderDAO
from ..domain.events.order_accepted import OrderAcceptedEvent
from ..domain.events.order_status_changed import OrderStatusChangedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..models.order import LocationEnum, Order, OrderStatus


class ProviderOrderService:
    """服务商订单服务"""

    @staticmethod
    async def list_available_orders(
        db: AsyncSession,
        location: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        keyword: Optional[str] = None,
    ) -> List[Order]:
        """浏览可用订单"""
        location_enum = LocationEnum(location) if location else None

        return await OrderDAO.get_available_orders(
            db=db, location=location_enum, min_price=min_price, max_price=max_price, keyword=keyword
        )

    @staticmethod
    async def get_available_order_detail(db: AsyncSession, order_id: int) -> Order:
        """获取可接单订单的详情（不需要认证，任何服务商都可以查看）"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # 只能查看状态为 pending 的订单
        if order.status != OrderStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This order is no longer available for acceptance",
            )

        return order

    @staticmethod
    async def accept_order(db: AsyncSession, provider_id: int, order_id: int) -> Order:
        """接受订单"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.status != OrderStatus.pending:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The order has already been accepted!")

        # 接受订单
        updated_order = await OrderDAO.accept_order(db, order_id, provider_id)

        # 发布订单接受事件
        event = OrderAcceptedEvent(
            order_id=order_id, customer_id=order.customer_id, provider_id=provider_id, timestamp=datetime.now(UTC)
        )
        await EventPublisher.publish_order_accepted(event)

        return updated_order

    @staticmethod
    async def update_order_status(db: AsyncSession, provider_id: int, order_id: int, new_status: str) -> Order:
        """更新订单状态"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.provider_id != provider_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied: not your order")

        # 验证状态转换
        new_status_enum = OrderStatus(new_status)

        if new_status_enum not in {OrderStatus.in_progress, OrderStatus.completed}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported status update")

        if new_status_enum == OrderStatus.in_progress and order.status != OrderStatus.accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Order must be accepted before starting"
            )

        if new_status_enum == OrderStatus.completed and order.status != OrderStatus.in_progress:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Order must be in progress before completing"
            )

        old_status = order.status.value

        # 更新订单状态
        updated_order = await OrderDAO.update_order_status(db, order_id, new_status_enum)

        # 发布订单状态变更事件
        event = OrderStatusChangedEvent(
            order_id=order_id,
            customer_id=order.customer_id,
            provider_id=provider_id,
            old_status=old_status,
            new_status=new_status,
            timestamp=datetime.now(UTC),
        )
        await EventPublisher.publish_order_status_changed(event)

        return updated_order

    @staticmethod
    async def get_order_history(db: AsyncSession, provider_id: int) -> List[Order]:
        """获取服务商订单历史"""
        return await OrderDAO.get_provider_orders(db, provider_id)

    @staticmethod
    async def get_order_detail(db: AsyncSession, provider_id: int, order_id: int) -> Order:
        """获取订单详情"""
        order = await OrderDAO.get_order_by_id(db, order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.provider_id != provider_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

        return order
