from datetime import UTC, datetime

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..dao.payment_dao import PaymentDAO
from ..dao.transaction_dao import TransactionDAO
from ..domain.events.payment_completed import PaymentCompletedEvent
from ..domain.events.payment_initiated import PaymentInitiatedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..models.payment import PaymentMethod, PaymentStatus
from ..models.transaction import TransactionType


class PaymentService:
    """Payment Service（简化版 - MockPayment）"""

    @staticmethod
    async def pay_order(db: AsyncSession, user_id: int, order_id: int, token: str) -> dict:
        """CustomerPaymentOrder（MockPayment，No需余额）"""

        # 1. Call Order Service GetOrderInformation
        async with httpx.AsyncClient() as client:
            order_response = await client.get(
                f"{settings.ORDER_SERVICE_URL}/customer/orders/my/{order_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            if order_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Order not found: {order_response.text}"
                )

            order = order_response.json()

        # 2. VerifyOrderStatus：OnlyWith当OrderStatus是 completed 且PaymentStatus是 unpaid When才能Payment
        if order["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="订单未完成，无法支付 / Order not completed, cannot pay"
            )

        if order.get("payment_status") != "unpaid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单不可支付，支付状态必须为 unpaid / Order cannot be paid, payment status must be unpaid",
            )

        # 3. Check是否AlreadyExistsPayment记录
        existing_payment = await PaymentDAO.get_payment_by_order_id(db, order_id)
        if existing_payment and existing_payment.status == PaymentStatus.completed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单已支付 / Order already paid")

        order_price = float(order["price"])

        # 4. Create Payment记录（使用MockPayment方式）
        payment = await PaymentDAO.create_payment(
            db=db,
            order_id=order_id,
            customer_id=user_id,
            provider_id=order.get("provider_id"),
            amount=order_price,
            payment_method=PaymentMethod.simulated,
        )

        # 5. PublishPayment发起Event
        await EventPublisher.publish_payment_initiated(
            PaymentInitiatedEvent(
                payment_id=payment.id,
                order_id=order_id,
                customer_id=user_id,
                amount=order_price,
                timestamp=datetime.now(UTC),
            )
        )

        # 6. MockPaymentSuccess - UpdatePaymentStatus为AlreadyComplete
        await PaymentDAO.update_payment_status(db, payment.id, PaymentStatus.completed)

        # 7. CreateTransaction记录（不含余额Information）
        await TransactionDAO.create_transaction(
            db=db,
            user_id=user_id,
            transaction_type=TransactionType.payment,
            amount=order_price,
            reference_id=payment.id,
            description=f"支付订单 {order_id}（模拟支付）",
        )

        # 8. Publish Payment Completed Event
        await EventPublisher.publish_payment_completed(
            PaymentCompletedEvent(
                payment_id=payment.id,
                order_id=order_id,
                customer_id=user_id,
                provider_id=order.get("provider_id"),
                amount=order_price,
                timestamp=datetime.now(UTC),
            )
        )

        return {
            "payment_id": payment.id,
            "order_id": order_id,
            "amount": order_price,
            "message": f"支付成功（模拟），订单 {order_id} 已支付",
        }
