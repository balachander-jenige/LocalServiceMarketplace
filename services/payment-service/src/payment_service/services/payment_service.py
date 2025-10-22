from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, UTC
import httpx

from ..dao.payment_dao import PaymentDAO
from ..dao.transaction_dao import TransactionDAO
from ..models.payment import PaymentStatus, PaymentMethod
from ..models.transaction import TransactionType
from ..domain.events.payment_initiated import PaymentInitiatedEvent
from ..domain.events.payment_completed import PaymentCompletedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..core.config import settings

class PaymentService:
    """支付服务（简化版 - 模拟支付）"""
    
    @staticmethod
    async def pay_order(
        db: AsyncSession,
        user_id: int,
        order_id: int,
        token: str
    ) -> dict:
        """客户支付订单（模拟支付，无需余额）"""
        
        # 1. 调用 Order Service 获取订单信息
        async with httpx.AsyncClient() as client:
            order_response = await client.get(
                f"{settings.ORDER_SERVICE_URL}/customer/orders/my/{order_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if order_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order not found: {order_response.text}"
                )
            
            order = order_response.json()
        
        # 2. 验证订单状态：只有当订单状态是 completed 且支付状态是 unpaid 时才能支付
        if order["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单未完成，无法支付 / Order not completed, cannot pay"
            )
        
        if order.get("payment_status") != "unpaid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单不可支付，支付状态必须为 unpaid / Order cannot be paid, payment status must be unpaid"
            )
        
        # 3. 检查是否已存在支付记录
        existing_payment = await PaymentDAO.get_payment_by_order_id(db, order_id)
        if existing_payment and existing_payment.status == PaymentStatus.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单已支付 / Order already paid"
            )
        
        order_price = float(order["price"])
        
        # 4. 创建支付记录（使用模拟支付方式）
        payment = await PaymentDAO.create_payment(
            db=db,
            order_id=order_id,
            customer_id=user_id,
            provider_id=order.get("provider_id"),
            amount=order_price,
            payment_method=PaymentMethod.simulated
        )
        
        # 5. 发布支付发起事件
        await EventPublisher.publish_payment_initiated(
            PaymentInitiatedEvent(
                payment_id=payment.id,
                order_id=order_id,
                customer_id=user_id,
                amount=order_price,
                timestamp=datetime.now(UTC)
            )
        )
        
        # 6. 模拟支付成功 - 更新支付状态为已完成
        await PaymentDAO.update_payment_status(db, payment.id, PaymentStatus.completed)
        
        # 7. 创建交易记录（不含余额信息）
        await TransactionDAO.create_transaction(
            db=db,
            user_id=user_id,
            transaction_type=TransactionType.payment,
            amount=order_price,
            reference_id=payment.id,
            description=f"支付订单 {order_id}（模拟支付）"
        )
        
        # 8. 发布支付完成事件
        await EventPublisher.publish_payment_completed(
            PaymentCompletedEvent(
                payment_id=payment.id,
                order_id=order_id,
                customer_id=user_id,
                provider_id=order.get("provider_id"),
                amount=order_price,
                timestamp=datetime.now(UTC)
            )
        )
        
        return {
            "payment_id": payment.id,
            "order_id": order_id,
            "amount": order_price,
            "message": f"支付成功（模拟），订单 {order_id} 已支付"
        }