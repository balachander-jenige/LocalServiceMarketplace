import json

from aio_pika import IncomingMessage


async def handle_order_completed(message: IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        print(f"Received order completed event: {data}")
        # Can在此处做后续Handle，如Allow评价等
