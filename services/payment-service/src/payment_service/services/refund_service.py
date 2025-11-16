from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dao.payment_dao import PaymentDAO
from ..dao.refund_dao import RefundDAO
from ..dao.transaction_dao import TransactionDAO
from ..domain.events.refund_processed import RefundProcessedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..models.refund import RefundStatus
from ..models.transaction import TransactionType


class RefundService:
    """Refund Service（简化版 - 不涉及余额）"""

    @staticmethod
    async def process_refund(db: AsyncSession, user_id: int, order_id: int, reason: str = None) -> dict:
        """Process Refund（简化版，不返还余额）"""
        # GetPayment记录
        payment = await PaymentDAO.get_payment_by_order_id(db, order_id)

        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        if payment.customer_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

        # Check是否AlreadyRefund
        existing_refund = await RefundDAO.get_refund_by_order_id(db, order_id)
        if existing_refund:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refund already processed")

        # Create Refund记录
        refund = await RefundDAO.create_refund(
            db=db,
            payment_id=payment.id,
            order_id=order_id,
            customer_id=user_id,
            amount=float(payment.amount),
            reason=reason,
        )

        # CreateTransaction记录（不含余额Information）
        await TransactionDAO.create_transaction(
            db=db,
            user_id=user_id,
            transaction_type=TransactionType.refund,
            amount=float(payment.amount),
            reference_id=refund.id,
            description=f"订单 {order_id} 退款（模拟）",
        )

        # UpdateRefundStatus为AlreadyComplete
        await RefundDAO.update_refund_status(db, refund.id, RefundStatus.completed)

        # PublishRefundHandleCompleteEvent
        await EventPublisher.publish_refund_processed(
            RefundProcessedEvent(
                refund_id=refund.id,
                order_id=order_id,
                customer_id=user_id,
                amount=float(payment.amount),
                timestamp=datetime.now(UTC),
            )
        )

        return {
            "refund_id": refund.id,
            "order_id": order_id,
            "amount": float(payment.amount),
            "status": RefundStatus.completed.value,
            "message": f"退款成功（模拟），已记录退款 {payment.amount} 元",
        }
