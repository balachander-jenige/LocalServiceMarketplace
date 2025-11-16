import json

from aio_pika import IncomingMessage

from ...core.mongodb import get_database


async def handle_payment_completed(message: IncomingMessage):
    """Handle Payment Completed Event"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        # NotificationCustomer
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Payment for order {data['order_id']} completed successfully.",
        )

        # Notification Service商
        await service.send_provider_notification(
            provider_id=data["provider_id"],
            order_id=data["order_id"],
            message=f"Payment for order {data['order_id']} received.",
        )


async def handle_payment_failed(message: IncomingMessage):
    """Handle Payment Failed Event"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"Payment for order {data['order_id']} failed. Please try again.",
        )
