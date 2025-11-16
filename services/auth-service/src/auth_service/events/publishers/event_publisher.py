from ...domain.events.user_registered import UserRegisteredEvent
from ...messaging.rabbitmq_client import rabbitmq_client


class EventPublisher:
    """Event Publisher"""

    @staticmethod
    async def publish_user_registered(event: UserRegisteredEvent):
        """Publish User Registered Event"""
        await rabbitmq_client.publish_event(
            exchange_name="user_events", routing_key="user.registered", message=event.model_dump_json()
        )
