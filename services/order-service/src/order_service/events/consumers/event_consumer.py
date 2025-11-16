from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.payment_event_handler import handle_payment_completed


async def start_consuming():
    """Start Consuming Events"""
    await rabbitmq_client.connect()

    # Listen ToPayment Completed Event
    await rabbitmq_client.consume_events(
        exchange_name="payment_events", routing_key="payment.completed", callback=handle_payment_completed
    )

    print("✅ Started consuming payment events")
