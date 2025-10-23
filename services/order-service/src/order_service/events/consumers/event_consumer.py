from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.payment_event_handler import handle_payment_completed

async def start_consuming():
    """开始消费事件"""
    await rabbitmq_client.connect()
    
    # 监听支付完成事件
    await rabbitmq_client.consume_events(
        exchange_name="payment_events",
        routing_key="payment.completed",
        callback=handle_payment_completed
    )
    
    print("✅ Started consuming payment events")