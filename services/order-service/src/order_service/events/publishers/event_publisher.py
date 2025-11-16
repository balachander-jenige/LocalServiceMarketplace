from ...domain.events.order_accepted import OrderAcceptedEvent
from ...domain.events.order_approved import OrderApprovedEvent
from ...domain.events.order_cancelled import OrderCancelledEvent
from ...domain.events.order_created import OrderCreatedEvent
from ...domain.events.order_rejected import OrderRejectedEvent
from ...domain.events.order_status_changed import OrderStatusChangedEvent
from ...messaging.rabbitmq_client import rabbitmq_client


class EventPublisher:
    """Event Publisher"""

    @staticmethod
    async def publish_order_created(event: OrderCreatedEvent):
        """Publish Order Created Event"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.created", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_accepted(event: OrderAcceptedEvent):
        """Publish Order Accepted Event"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.accepted", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_status_changed(event: OrderStatusChangedEvent):
        """Publish Order Status Changed Event"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.status_changed", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_cancelled(event: OrderCancelledEvent):
        """Publish Order Cancelled Event"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.cancelled", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_approved(event: OrderApprovedEvent):
        """PublishOrder审批通过Event"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.approved", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_rejected(event: OrderRejectedEvent):
        """PublishOrder审批RejectEvent"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.rejected", message=event.model_dump_json()
        )
