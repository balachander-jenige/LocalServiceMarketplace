from ...domain.events.order_accepted import OrderAcceptedEvent
from ...domain.events.order_approved import OrderApprovedEvent
from ...domain.events.order_cancelled import OrderCancelledEvent
from ...domain.events.order_created import OrderCreatedEvent
from ...domain.events.order_rejected import OrderRejectedEvent
from ...domain.events.order_status_changed import OrderStatusChangedEvent
from ...messaging.rabbitmq_client import rabbitmq_client


class EventPublisher:
    """事件发布器"""

    @staticmethod
    async def publish_order_created(event: OrderCreatedEvent):
        """发布订单创建事件"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.created", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_accepted(event: OrderAcceptedEvent):
        """发布订单接受事件"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.accepted", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_status_changed(event: OrderStatusChangedEvent):
        """发布订单状态变更事件"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.status_changed", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_cancelled(event: OrderCancelledEvent):
        """发布订单取消事件"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.cancelled", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_approved(event: OrderApprovedEvent):
        """发布订单审批通过事件"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.approved", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_order_rejected(event: OrderRejectedEvent):
        """发布订单审批拒绝事件"""
        await rabbitmq_client.publish_event(
            exchange_name="order_events", routing_key="order.rejected", message=event.model_dump_json()
        )
