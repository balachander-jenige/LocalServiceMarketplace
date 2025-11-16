from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.order_event_handler import handle_order_completed


async def start_consuming():
    """Start Consuming Events"""
    await rabbitmq_client.connect()

    # Listen ToOrderCompleteEvent
    await rabbitmq_client.consume_events(
        exchange_name="order_events", routing_key="order.status_changed", callback=handle_order_completed
    )

    print("✅ Started consuming order events")
