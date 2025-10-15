from ...messaging.rabbitmq_client import rabbitmq_client
from ...domain.events.user_registered import UserRegisteredEvent

class EventPublisher:
    """事件发布器"""
    
    @staticmethod
    async def publish_user_registered(event: UserRegisteredEvent):
        """发布用户注册事件"""
        await rabbitmq_client.publish_event(
            exchange_name="user_events",
            routing_key="user.registered",
            message=event.dict()
        )