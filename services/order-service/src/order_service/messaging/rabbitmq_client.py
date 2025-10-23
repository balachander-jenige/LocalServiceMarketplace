import json

import aio_pika

from ..core.config import settings


class RabbitMQClient:
    """RabbitMQ 客户端"""

    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        """连接到 RabbitMQ"""
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        print(f"✅ Connected to RabbitMQ: {settings.RABBITMQ_URL}")

    async def publish_event(self, exchange_name: str, routing_key: str, message: dict):
        """发布事件"""
        if not self.channel:
            await self.connect()

        exchange = await self.channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

        await exchange.publish(
            aio_pika.Message(body=message.encode(), content_type="application/json"), routing_key=routing_key
        )

    async def consume_events(self, exchange_name: str, routing_key: str, callback):
        """消费事件"""
        if not self.channel:
            await self.connect()

        exchange = await self.channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

        queue = await self.channel.declare_queue("", exclusive=True)
        await queue.bind(exchange, routing_key=routing_key)

        await queue.consume(callback)

    async def close(self):
        """关闭连接"""
        if self.connection:
            await self.connection.close()
            print("✅ Closed RabbitMQ connection")


# 全局实例
rabbitmq_client = RabbitMQClient()
