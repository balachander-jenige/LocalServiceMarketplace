from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, UTC
import httpx
from decimal import Decimal

from ..dao.payment_dao import PaymentDAO
from ..dao.transaction_dao import TransactionDAO
from ..models.payment import PaymentStatus, PaymentMethod, Payment
from ..models.transaction import TransactionType
from ..domain.events.payment_initiated import PaymentInitiatedEvent
from ..domain.events.payment_completed import PaymentCompletedEvent
from ..domain.events.payment_failed import PaymentFailedEvent
from ..events.publishers.event_publisher import EventPublisher
from ..core.config import settings

class PaymentService:
    """支付服务"""
    
    @staticmethod
    async def recharge_balance(
        db: AsyncSession,
        user_id: int,
        amount: float,
        token: str
    ) -> dict:
        """客户充值余额"""
        # 调用 User Service 获取当前余额
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/customer/profile/{user_id}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer profile not found"
                )
            
            profile = response.json()
            balance_before = float(profile.get("balance", 0))
            balance_after = balance_before + amount
        
        # 创建交易记录
        transaction = await TransactionDAO.create_transaction(
            db=db,
            user_id=user_id,
            transaction_type=TransactionType.recharge,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f"充值 {amount} 元"
        )
        
        # 更新 User Service 的余额（通过 HTTP 调用）
        async with httpx.AsyncClient() as client:
            update_response = await client.put(
                f"{settings.USER_SERVICE_URL}/customer/profile/me",
                json={"balance": balance_after},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if update_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update user balance: {update_response.text}"
                )
        
        return {
            "transaction_id": transaction.id,
            "balance": balance_after,
            "message": f"充值成功，当前余额为 {balance_after}"
        }
    
    @staticmethod
    async def pay_order(
        db: AsyncSession,
        user_id: int,
        order_id: int,
        token: str
    ) -> dict:
        """客户支付订单"""
        # 调用 Order Service 获取订单信息
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
        
        # 验证订单状态：只有当订单状态是 completed 且支付状态是 unpaid 时才能支付
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
        
        # 检查是否已存在支付记录
        existing_payment = await PaymentDAO.get_payment_by_order_id(db, order_id)
        if existing_payment and existing_payment.status == PaymentStatus.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单已支付 / Order already paid"
            )
        
        order_price = float(order["price"])
        
        # 获取客户余额
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
        
        # 检查余额是否足够
        if balance_before < order_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="余额不足，请充值 / Insufficient balance, please recharge"
            )
        
        balance_after = balance_before - order_price
        
        # 创建支付记录
        payment = await PaymentDAO.create_payment(
            db=db,
            order_id=order_id,
            customer_id=user_id,
            provider_id=order.get("provider_id"),
            amount=order_price,
            payment_method=PaymentMethod.balance
        )
        
        # 发布支付发起事件
        await EventPublisher.publish_payment_initiated(
            PaymentInitiatedEvent(
                payment_id=payment.id,
                order_id=order_id,
                customer_id=user_id,
                amount=order_price,
                timestamp=datetime.now(UTC)
            )
        )
        
        # 创建交易记录
        transaction = await TransactionDAO.create_transaction(
            db=db,
            user_id=user_id,
            transaction_type=TransactionType.payment,
            amount=order_price,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_id=payment.id,
            description=f"支付订单 {order_id}"
        )
        
        # 更新支付状态为已完成
        await PaymentDAO.update_payment_status(db, payment.id, PaymentStatus.completed)
        
        # 更新 User Service 的余额
        async with httpx.AsyncClient() as client:
            update_response = await client.put(
                f"{settings.USER_SERVICE_URL}/customer/profile/me",
                json={"balance": balance_after},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if update_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update user balance: {update_response.text}"
                )
        
        # 发布支付完成事件
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
            "balance": balance_after,
            "message": f"支付成功，订单 {order_id} 已支付"
        }