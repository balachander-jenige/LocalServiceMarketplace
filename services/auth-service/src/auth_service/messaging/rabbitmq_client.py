import json

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

    async def publish_event(self, exchange_name: str, routing_key: str, message: dict):
        """Publish Event"""
        if not self.channel:
            await self.connect()

        exchange = await self.channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

        await exchange.publish(
            aio_pika.Message(body=message.encode(), content_type="application/json"), routing_key=routing_key
        )

    async def close(self):
        """Close Connection"""
        if self.connection:
            await self.connection.close()


# Global Instance
rabbitmq_client = RabbitMQClient()
