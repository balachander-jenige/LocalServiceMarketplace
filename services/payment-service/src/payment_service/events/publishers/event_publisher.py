from ...domain.events.payment_completed import PaymentCompletedEvent
from ...domain.events.payment_failed import PaymentFailedEvent
from ...domain.events.payment_initiated import PaymentInitiatedEvent
from ...messaging.rabbitmq_client import rabbitmq_client


class EventPublisher:
    """事件发布器"""

    @staticmethod
    async def publish_payment_initiated(event: PaymentInitiatedEvent):
        """发布支付发起事件"""
        await rabbitmq_client.publish_event(
            exchange_name="payment_events", routing_key="payment.initiated", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_payment_completed(event: PaymentCompletedEvent):
        """发布支付完成事件"""
        await rabbitmq_client.publish_event(
            exchange_name="payment_events", routing_key="payment.completed", message=event.model_dump_json()
        )

    @staticmethod
    async def publish_payment_failed(event: PaymentFailedEvent):
        """发布支付失败事件"""
        await rabbitmq_client.publish_event(
            exchange_name="payment_events", routing_key="payment.failed", message=event.model_dump_json()
        )
