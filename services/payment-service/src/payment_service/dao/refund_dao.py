from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from datetime import datetime, UTC

from ..models.refund import Refund, RefundStatus

class RefundDAO:
    """退款数据访问对象"""
    
    @staticmethod
    async def create_refund(
        db: AsyncSession,
        payment_id: int,
        order_id: int,
        customer_id: int,
        amount: float,
        reason: Optional[str] = None
    ) -> Refund:
        """创建退款记录"""
        refund = Refund(
            payment_id=payment_id,
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            status=RefundStatus.pending,
            reason=reason,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        db.add(refund)
        await db.commit()
        await db.refresh(refund)
        return refund
    
    @staticmethod
    async def get_refund_by_id(db: AsyncSession, refund_id: int) -> Optional[Refund]:
        """根据 ID 获取退款记录"""
        return await db.get(Refund, refund_id)
    
    @staticmethod
    async def get_refund_by_order_id(db: AsyncSession, order_id: int) -> Optional[Refund]:
        """根据订单 ID 获取退款记录"""
        result = await db.execute(
            select(Refund).where(Refund.order_id == order_id)
        )
        return result.scalars().first()
    
    @staticmethod
    async def update_refund_status(
        db: AsyncSession,
        refund_id: int,
        status: RefundStatus
    ) -> Optional[Refund]:
        """更新退款状态"""
        refund = await db.get(Refund, refund_id)
        if refund:
            refund.status = status
            refund.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(refund)
        return refund