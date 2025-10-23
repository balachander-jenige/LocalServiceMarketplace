from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.order_event_handler import handle_order_completed

async def start_consuming():
    """开始消费事件"""
    await rabbitmq_client.connect()
    
    # 监听订单完成事件
    await rabbitmq_client.consume_events(
        exchange_name="order_events",
        routing_key="order.status_changed",
        callback=handle_order_completed
    )
    
    print("✅ Started consuming order events")