import json

from aio_pika import IncomingMessage

from ...core.mongodb import get_database


async def handle_order_created(message: IncomingMessage):
    """Handle Order Created Event"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"You have successfully published the order: {data['order_id']}.",
        )


async def handle_order_accepted(message: IncomingMessage):
    """Handle Order Accepted Event"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        # NotificationCustomer
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Your order: {data['order_id']} has been accepted by provider: {data['provider_id']}.",
        )

        # Notification Service商
        await service.send_provider_notification(
            provider_id=data["provider_id"],
            order_id=data["order_id"],
            message=f"You have successfully accepted the order: {data['order_id']}.",
        )


async def handle_order_status_changed(message: IncomingMessage):
    """HandleOrder Status Changed Event"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        # NotificationCustomer
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Order {data['order_id']} status updated to {data['new_status']}.",
        )

        # Notification Service商
        if data.get("provider_id"):
            await service.send_provider_notification(
                provider_id=data["provider_id"],
                order_id=data["order_id"],
                message=f"Order {data['order_id']} status updated to {data['new_status']}.",
            )


async def handle_order_cancelled(message: IncomingMessage):
    """Handle Order Cancelled Event"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        # NotificationCustomer
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"You have successfully cancelled the order: {data['order_id']}.",
        )

        # 如果WithProvider，也Notification Service商
        if data.get("provider_id"):
            await service.send_provider_notification(
                provider_id=data["provider_id"],
                order_id=data["order_id"],
                message=f"Order {data['order_id']} has been cancelled by customer.",
            )


async def handle_order_approved(message: IncomingMessage):
    """HandleOrder审核通过Event"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        # NotificationCustomerOrder审核通过
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Your order {data['order_id']} has been approved by admin. It is now available for providers to accept.",
        )


async def handle_order_rejected(message: IncomingMessage):
    """HandleOrder审核RejectEvent"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        # NotificationCustomerOrder审核被Reject，ContainsReject原因
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Your order {data['order_id']} has been rejected by admin. Reason: {data['reject_reason']}",
        )
