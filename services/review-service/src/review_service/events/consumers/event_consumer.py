from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.review_event_handler import handle_review_created
from ..handlers.order_completed_handler import handle_order_completed

async def start_consuming():
    await rabbitmq_client.connect()
    await rabbitmq_client.consume_events(
        exchange_name="review_events",
        routing_key="review.created",
        callback=handle_review_created
    )
    await rabbitmq_client.consume_events(
        exchange_name="order_events",
        routing_key="order.completed",
        callback=handle_order_completed
    )
    print("✅ Started consuming review and order events")