from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from datetime import datetime, UTC
import uuid

from ..models.payment import Payment, PaymentStatus, PaymentMethod

class PaymentDAO:
    """支付数据访问对象"""
    
    @staticmethod
    async def create_payment(
        db: AsyncSession,
        order_id: int,
        customer_id: int,
        provider_id: Optional[int],
        amount: float,
        payment_method: PaymentMethod = PaymentMethod.simulated
    ) -> Payment:
        """创建支付记录"""
        payment = Payment(
            order_id=order_id,
            customer_id=customer_id,
            provider_id=provider_id,
            amount=amount,
            payment_method=payment_method,
            status=PaymentStatus.pending,
            transaction_id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment
    
    @staticmethod
    async def get_payment_by_id(db: AsyncSession, payment_id: int) -> Optional[Payment]:
        """根据 ID 获取支付记录"""
        return await db.get(Payment, payment_id)
    
    @staticmethod
    async def get_payment_by_order_id(db: AsyncSession, order_id: int) -> Optional[Payment]:
        """根据订单 ID 获取支付记录"""
        result = await db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalars().first()
    
    @staticmethod
    async def update_payment_status(
        db: AsyncSession,
        payment_id: int,
        status: PaymentStatus
    ) -> Optional[Payment]:
        """更新支付状态"""
        payment = await db.get(Payment, payment_id)
        if payment:
            payment.status = status
            payment.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(payment)
        return payment


        
    
    @staticmethod
    async def get_user_payments(
        db: AsyncSession,
        user_id: int
    ) -> List[Payment]:
        """获取用户的支付记录"""
        result = await db.execute(
            select(Payment)
            .where(Payment.customer_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())