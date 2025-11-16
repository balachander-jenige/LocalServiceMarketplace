from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.order_event_handler import (
    handle_order_accepted,
    handle_order_approved,
    handle_order_cancelled,
    handle_order_created,
    handle_order_rejected,
    handle_order_status_changed,
)
from ..handlers.payment_event_handler import handle_payment_completed, handle_payment_failed
from ..handlers.review_event_handler import handle_review_created


async def start_consuming():
    """开始ConsumeAllEvent"""
    await rabbitmq_client.connect()

    # Listen ToOrderEvent
    await rabbitmq_client.consume_events(
        exchange_name="order_events", routing_key="order.created", callback=handle_order_created
    )
    await rabbitmq_client.consume_events(
        exchange_name="order_events", routing_key="order.accepted", callback=handle_order_accepted
    )
    await rabbitmq_client.consume_events(
        exchange_name="order_events", routing_key="order.status_changed", callback=handle_order_status_changed
    )
    await rabbitmq_client.consume_events(
        exchange_name="order_events", routing_key="order.cancelled", callback=handle_order_cancelled
    )
    await rabbitmq_client.consume_events(
        exchange_name="order_events", routing_key="order.approved", callback=handle_order_approved
    )
    await rabbitmq_client.consume_events(
        exchange_name="order_events", routing_key="order.rejected", callback=handle_order_rejected
    )

    # Listen ToPaymentEvent
    await rabbitmq_client.consume_events(
        exchange_name="payment_events", routing_key="payment.completed", callback=handle_payment_completed
    )
    await rabbitmq_client.consume_events(
        exchange_name="payment_events", routing_key="payment.failed", callback=handle_payment_failed
    )

    # Listen To评价Event
    await rabbitmq_client.consume_events(
        exchange_name="review_events", routing_key="review.created", callback=handle_review_created
    )

    print("✅ Started consuming all events")
