import aio_pika

from ..core.config import settings


class RabbitMQClient:
    """RabbitMQ Client"""

    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        """Connect to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        print(f"✅ Connected to RabbitMQ: {settings.RABBITMQ_URL}")

    async def publish_event(self, exchange_name: str, routing_key: str, message: str):
        """Publish Event（message Already经是 JSON 字符串）"""
        if not self.channel:
            await self.connect()

        exchange = await self.channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

        await exchange.publish(
            aio_pika.Message(body=message.encode(), content_type="application/json"), routing_key=routing_key
        )

    async def consume_events(self, exchange_name: str, routing_key: str, callback):
        """ConsumeEvent"""
        if not self.channel:
            await self.connect()

        exchange = await self.channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

        queue = await self.channel.declare_queue("", exclusive=True)
        await queue.bind(exchange, routing_key=routing_key)

        await queue.consume(callback)

    async def close(self):
        """Close Connection"""
        if self.connection:
            await self.connection.close()
            print("✅ Closed RabbitMQ connection")


# Global Instance
rabbitmq_client = RabbitMQClient()
