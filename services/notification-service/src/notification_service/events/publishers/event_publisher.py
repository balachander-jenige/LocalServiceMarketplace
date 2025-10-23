from ...domain.events.notification_sent import NotificationSentEvent
from ...messaging.rabbitmq_client import rabbitmq_client


class EventPublisher:
    @staticmethod
    async def publish_notification_sent(event: NotificationSentEvent):
        await rabbitmq_client.publish_event(
            exchange_name="notification_events", routing_key="notification.sent", message=event.model_dump_json()
        )
