from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, UTC
import httpx

from ..dao.refund_dao import RefundDAO
from ..dao.payment_dao import PaymentDAO
from ..dao.transaction_dao import TransactionDAO
from ..models.refund import RefundStatus
from ..models.transaction import TransactionType
from ..domain.events.refund_processed import RefundProcessedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..core.config import settings

class RefundService:
    """退款服务"""
    
    @staticmethod
    async def process_refund(
        db: AsyncSession,
        user_id: int,
        order_id: int,
        reason: str = None
    ) -> dict:
        """处理退款"""
        # 获取支付记录
        payment = await PaymentDAO.get_payment_by_order_id(db, order_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.customer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # 检查是否已退款
        existing_refund = await RefundDAO.get_refund_by_order_id(db, order_id)
        if existing_refund:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund already processed"
            )
        
        # 创建退款记录
        refund = await RefundDAO.create_refund(
            db=db,
            payment_id=payment.id,
            order_id=order_id,
            customer_id=user_id,
            amount=float(payment.amount),
            reason=reason
        )
        
        # 获取客户当前余额
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(
                f"{settings.USER_SERVICE_URL}/customer/profile/{user_id}"
            )
            
            if profile_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer profile not found"
                )
            
            profile = profile_response.json()
            balance_before = float(profile.get("balance", 0))
            balance_after = balance_before + float(payment.amount)
        
        # 创建交易记录
        await TransactionDAO.create_transaction(
            db=db,
            user_id=user_id,
            transaction_type=TransactionType.refund,
            amount=float(payment.amount),
            balance_before=balance_before,
            balance_after=balance_after,
            reference_id=refund.id,
            description=f"订单 {order_id} 退款"
        )
        
        # 更新退款状态
        await RefundDAO.update_refund_status(db, refund.id, RefundStatus.completed)
        
        # 更新 User Service 的余额
        async with httpx.AsyncClient() as client:
            await client.put(
                f"{settings.USER_SERVICE_URL}/customer/profile/me",
                json={"balance": balance_after}
            )
        
        # 发布退款处理完成事件
        await EventPublisher.publish_refund_processed(
            RefundProcessedEvent(
                refund_id=refund.id,
                order_id=order_id,
                customer_id=user_id,
                amount=float(payment.amount),
                timestamp=datetime.now(UTC)
            )
        )
        
        return {
            "refund_id": refund.id,
            "order_id": order_id,
            "amount": float(payment.amount),
            "status": RefundStatus.completed.value,
            "message": f"退款成功，已退款 {payment.amount} 元"
        }