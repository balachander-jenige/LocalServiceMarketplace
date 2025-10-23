import json
from aio_pika import IncomingMessage
from ...core.database import get_db
from ...dao.order_dao import OrderDAO
from ...models.order import PaymentStatus

async def handle_payment_completed(message: IncomingMessage):
    """
    处理支付完成事件
    Handle payment completed event
    """
    async with message.process():
        data = json.loads(message.body.decode())
        order_id = data.get("order_id")
        
        # 获取数据库会话（需要手动管理）
        from ...core.database import async_session_maker
        async with async_session_maker() as db:
            # 更新订单支付状态
            await OrderDAO.update_payment_status(db, order_id, PaymentStatus.paid)
            print(f"✅ Updated payment status for order {order_id} to paid")