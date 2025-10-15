from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, UTC

from ..models.order import Order, OrderStatus, PaymentStatus, LocationEnum

class OrderDAO:
    """订单数据访问对象"""
    
    @staticmethod
    async def create_order(
        db: AsyncSession,
        customer_id: int,
        title: str,
        description: Optional[str],
        price: float,
        location: LocationEnum,
        address: Optional[str]
    ) -> Order:
        """创建订单"""
        order = Order(
            customer_id=customer_id,
            title=title,
            description=description,
            price=price,
            location=location,
            address=address,
            status=OrderStatus.pending,
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order
    
    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
        """根据 ID 获取订单"""
        return await db.get(Order, order_id)
    
    @staticmethod
    async def get_customer_orders(
        db: AsyncSession,
        customer_id: int,
        statuses: Optional[List[OrderStatus]] = None
    ) -> List[Order]:
        """获取客户的订单列表"""
        query = select(Order).where(Order.customer_id == customer_id)
        
        if statuses:
            query = query.where(Order.status.in_(statuses))
        
        query = query.order_by(Order.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_provider_orders(db: AsyncSession, provider_id: int) -> List[Order]:
        """获取服务商的订单列表"""
        result = await db.execute(
            select(Order)
            .where(Order.provider_id == provider_id)
            .order_by(Order.updated_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_available_orders(
        db: AsyncSession,
        location: Optional[LocationEnum] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        keyword: Optional[str] = None
    ) -> List[Order]:
        """获取可用订单列表（pending 状态）"""
        query = select(Order).where(Order.status == OrderStatus.pending)
        
        if location:
            query = query.where(Order.location == location)
        if min_price is not None:
            query = query.where(Order.price >= min_price)
        if max_price is not None:
            query = query.where(Order.price <= max_price)
        if keyword:
            like_expr = f"%{keyword.strip()}%"
            query = query.where(
                or_(
                    Order.title.ilike(like_expr),
                    Order.description.ilike(like_expr)
                )
            )
        
        query = query.order_by(Order.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: int,
        new_status: OrderStatus
    ) -> Optional[Order]:
        """更新订单状态"""
        order = await db.get(Order, order_id)
        if order:
            order.status = new_status
            order.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(order)
        return order
    
    @staticmethod
    async def accept_order(
        db: AsyncSession,
        order_id: int,
        provider_id: int
    ) -> Optional[Order]:
        """接受订单"""
        order = await db.get(Order, order_id)
        if order:
            order.provider_id = provider_id
            order.status = OrderStatus.accepted
            order.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(order)
        return order
    
    @staticmethod
    async def update_payment_status(
        db: AsyncSession,
        order_id: int,
        payment_status: PaymentStatus
    ) -> Optional[Order]:
        """更新支付状态"""
        order = await db.get(Order, order_id)
        if order:
            order.payment_status = payment_status
            order.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(order)
        return order