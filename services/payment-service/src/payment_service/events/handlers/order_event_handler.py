import json
from aio_pika import IncomingMessage

async def handle_order_completed(message: IncomingMessage):
    """
    处理订单完成事件（可选：自动触发支付流程）
    Handle order completed event (optional: auto-trigger payment process)
    """
    async with message.process():
        data = json.loads(message.body.decode())
        order_id = data.get("order_id")
        
        print(f"✅ Received order completed event for order {order_id}")
        # TODO: 可以在这里实现自动支付逻辑
        # TODO: Can implement auto-payment logic here