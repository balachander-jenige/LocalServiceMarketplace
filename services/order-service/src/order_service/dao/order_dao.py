from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.order import LocationEnum, Order, OrderStatus, PaymentStatus, ServiceType


class OrderDAO:
    """OrderData Access Object"""

    @staticmethod
    async def create_order(
        db: AsyncSession,
        customer_id: int,
        title: str,
        description: Optional[str],
        service_type: ServiceType,
        price: float,
        location: LocationEnum,
        address: Optional[str],
        service_start_time: Optional[datetime] = None,
        service_end_time: Optional[datetime] = None,
    ) -> Order:
        """Create Order"""
        order = Order(
            customer_id=customer_id,
            title=title,
            description=description,
            service_type=service_type,
            price=price,
            location=location,
            address=address,
            service_start_time=service_start_time,
            service_end_time=service_end_time,
            status=OrderStatus.pending_review,  # 新Order默认为待审核Status
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
        """By ID GetOrder"""
        return await db.get(Order, order_id)

    @staticmethod
    async def get_customer_orders(
        db: AsyncSession, customer_id: int, statuses: Optional[List[OrderStatus]] = None
    ) -> List[Order]:
        """GetCustomer的OrderList"""
        query = select(Order).where(Order.customer_id == customer_id)

        if statuses:
            query = query.where(Order.status.in_(statuses))

        query = query.order_by(Order.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_provider_orders(db: AsyncSession, provider_id: int) -> List[Order]:
        """GetProvider的OrderList"""
        result = await db.execute(
            select(Order).where(Order.provider_id == provider_id).order_by(Order.updated_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_available_orders(
        db: AsyncSession,
        location: Optional[LocationEnum] = None,
        service_type: Optional[ServiceType] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        keyword: Optional[str] = None,
    ) -> List[Order]:
        """GetCan用OrderList（pending Status）"""
        query = select(Order).where(Order.status == OrderStatus.pending)

        if location:
            query = query.where(Order.location == location)
        if service_type:
            query = query.where(Order.service_type == service_type)
        if min_price is not None:
            query = query.where(Order.price >= min_price)
        if max_price is not None:
            query = query.where(Order.price <= max_price)
        if keyword:
            like_expr = f"%{keyword.strip()}%"
            query = query.where(or_(Order.title.ilike(like_expr), Order.description.ilike(like_expr)))

        query = query.order_by(Order.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_order_status(db: AsyncSession, order_id: int, new_status: OrderStatus) -> Optional[Order]:
        """Update Order Status"""
        order = await db.get(Order, order_id)
        if order:
            order.status = new_status
            order.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(order)
        return order

    @staticmethod
    async def accept_order(db: AsyncSession, order_id: int, provider_id: int) -> Optional[Order]:
        """Accept Order"""
        order = await db.get(Order, order_id)
        if order:
            order.provider_id = provider_id
            order.status = OrderStatus.accepted
            order.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(order)
        return order

    @staticmethod
    async def update_payment_status(db: AsyncSession, order_id: int, payment_status: PaymentStatus) -> Optional[Order]:
        """UpdatePaymentStatus"""
        order = await db.get(Order, order_id)
        if order:
            order.payment_status = payment_status
            order.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(order)
        return order

    @staticmethod
    async def get_all_orders(db: AsyncSession) -> List[Order]:
        """Get All Orders（Admin）"""
        result = await db.execute(select(Order).order_by(Order.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_orders_by_status(db: AsyncSession, status: OrderStatus) -> List[Order]:
        """ByStatusGet Order List（Admin）"""
        result = await db.execute(select(Order).where(Order.status == status).order_by(Order.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_order(db: AsyncSession, order_id: int, **kwargs: Any) -> Optional[Order]:
        """UpdateOrderFields（Admin）"""
        order = await db.get(Order, order_id)
        if order:
            for key, value in kwargs.items():
                if hasattr(order, key):
                    setattr(order, key, value)
            order.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(order)
        return order

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: int) -> bool:
        """DeleteOrder（Admin）"""
        order = await db.get(Order, order_id)
        if order:
            await db.delete(order)
            await db.commit()
            return True
        return False
