import json

from aio_pika import IncomingMessage

from ...core.mongodb import get_database


async def handle_review_created(message: IncomingMessage):
    """Handle评价CreateEvent"""
    from ...services.notification_service import NotificationService

    async with message.process():
        data = json.loads(message.body.decode())
        db = get_database()
        service = NotificationService(db)

        # NotificationCustomer
        await service.send_customer_notification(
            customer_id=data["customer_id"],
            order_id=data["order_id"],
            message=f"You have successfully reviewed order {data['order_id']}.",
        )

        # Notification Service商
        await service.send_provider_notification(
            provider_id=data["provider_id"],
            order_id=data["order_id"],
            message=f"Customer has reviewed your order {data['order_id']} with {data['stars']} stars.",
        )
