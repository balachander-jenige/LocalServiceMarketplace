import json
from aio_pika import IncomingMessage
from ...core.mongodb import get_database
from ...services.notification_service import NotificationService

async def handle_order_created(message: IncomingMessage):
    """处理订单创建事件"""
    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)
        
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"You have successfully published the order: {data['order_id']}."
        )

async def handle_order_accepted(message: IncomingMessage):
    """处理订单接受事件"""
    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)
        
        # 通知客户
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Your order: {data['order_id']} has been accepted by provider: {data['provider_id']}."
        )
        
        # 通知服务商
        await service.send_provider_notification(
            provider_id=data["provider_id"],
            order_id=data["order_id"],
            message=f"You have successfully accepted the order: {data['order_id']}."
        )

async def handle_order_status_changed(message: IncomingMessage):
    """处理订单状态变更事件"""
    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)
        
        # 通知客户
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Order {data['order_id']} status updated to {data['new_status']}."
        )
        
        # 通知服务商
        if data.get("provider_id"):
            await service.send_provider_notification(
                provider_id=data["provider_id"],
                order_id=data["order_id"],
                message=f"Order {data['order_id']} status updated to {data['new_status']}."
            )

async def handle_order_cancelled(message: IncomingMessage):
    """处理订单取消事件"""
    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)
        
        # 通知客户
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"You have successfully cancelled the order: {data['order_id']}."
        )
        
        # 如果有服务商，也通知服务商
        if data.get("provider_id"):
            await service.send_provider_notification(
                provider_id=data["provider_id"],
                order_id=data["order_id"],
                message=f"Order {data['order_id']} has been cancelled by customer."
            )

async def handle_order_approved(message: IncomingMessage):
    """处理订单审核通过事件"""
    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)
        
        # 通知客户订单审核通过
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Your order {data['order_id']} has been approved by admin. It is now available for providers to accept."
        )

async def handle_order_rejected(message: IncomingMessage):
    """处理订单审核拒绝事件"""
    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)
        
        # 通知客户订单审核被拒绝，包含拒绝原因
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Your order {data['order_id']} has been rejected by admin. Reason: {data['reject_reason']}"
        )