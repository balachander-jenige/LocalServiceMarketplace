from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.user_registered_handler import handle_user_registered

async def start_consuming():
    """开始消费事件"""
    await rabbitmq_client.connect()
    
    # 监听用户注册事件
    await rabbitmq_client.consume_events(
        exchange_name="user_events",
        routing_key="user.registered",
        callback=handle_user_registered
    )
    
    print("✅ Started consuming user events")