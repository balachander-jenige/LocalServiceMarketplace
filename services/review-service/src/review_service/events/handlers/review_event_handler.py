import json
from aio_pika import IncomingMessage

async def handle_review_created(message: IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        print(f"Received review created event: {data}")
        # 可在此处做后续处理，如通知等