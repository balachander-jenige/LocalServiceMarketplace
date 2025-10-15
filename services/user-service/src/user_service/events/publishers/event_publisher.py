from ...messaging.rabbitmq_client import rabbitmq_client
from ...domain.events.profile_created import ProfileCreatedEvent
from ...domain.events.profile_updated import ProfileUpdatedEvent

class EventPublisher:
    """事件发布器"""
    
    @staticmethod
    async def publish_profile_created(event: ProfileCreatedEvent):
        """发布用户资料创建事件"""
        await rabbitmq_client.publish_event(
            exchange_name="profile_events",
            routing_key=f"profile.{event.profile_type}.created",
            message=event.model_dump_json()
        )
    
    @staticmethod
    async def publish_profile_updated(event: ProfileUpdatedEvent):
        """发布用户资料更新事件"""
        await rabbitmq_client.publish_event(
            exchange_name="profile_events",
            routing_key=f"profile.{event.profile_type}.updated",
            message=event.model_dump_json()
        )