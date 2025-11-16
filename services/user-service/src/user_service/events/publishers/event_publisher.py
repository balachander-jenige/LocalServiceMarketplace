from ...domain.events.profile_created import ProfileCreatedEvent
from ...domain.events.profile_updated import ProfileUpdatedEvent
from ...messaging.rabbitmq_client import rabbitmq_client


class EventPublisher:
    """Event Publisher"""

    @staticmethod
    async def publish_profile_created(event: ProfileCreatedEvent):
        """PublishUserProfileCreateEvent"""
        await rabbitmq_client.publish_event(
            exchange_name="profile_events",
            routing_key=f"profile.{event.profile_type}.created",
            message=event.model_dump_json(),
        )

    @staticmethod
    async def publish_profile_updated(event: ProfileUpdatedEvent):
        """PublishUserProfileUpdateEvent"""
        await rabbitmq_client.publish_event(
            exchange_name="profile_events",
            routing_key=f"profile.{event.profile_type}.updated",
            message=event.model_dump_json(),
        )
