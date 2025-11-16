from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..dao.customer_inbox_dao import CustomerInboxDAO
from ..dao.provider_inbox_dao import ProviderInboxDAO
from ..domain.events.notification_sent import NotificationSentEvent
from ..events.publishers.event_publisher import EventPublisher
from ..models.customer_inbox import CustomerInbox
from ..models.provider_inbox import ProviderInbox


class NotificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.customer_dao = CustomerInboxDAO(db)
        self.provider_dao = ProviderInboxDAO(db)

    async def send_customer_notification(self, customer_id: int, order_id: int, message: str):
        """发送CustomerNotification"""
        notification = CustomerInbox(
            customer_id=customer_id, order_id=order_id, message=message, created_at=datetime.utcnow(), is_read=False
        )
        await self.customer_dao.create(notification)

        # PublishNotificationAlready发送Event
        event = NotificationSentEvent(
            recipient_id=customer_id,
            recipient_type="customer",
            order_id=order_id,
            message=message,
            timestamp=datetime.utcnow(),
        )
        await EventPublisher.publish_notification_sent(event)

    async def send_provider_notification(self, provider_id: int, order_id: int, message: str):
        """发送ProviderNotification"""
        notification = ProviderInbox(
            provider_id=provider_id, order_id=order_id, message=message, created_at=datetime.utcnow(), is_read=False
        )
        await self.provider_dao.create(notification)

        # PublishNotificationAlready发送Event
        event = NotificationSentEvent(
            recipient_id=provider_id,
            recipient_type="provider",
            order_id=order_id,
            message=message,
            timestamp=datetime.utcnow(),
        )
        await EventPublisher.publish_notification_sent(event)

    async def get_customer_inbox(self, customer_id: int):
        """GetCustomerInbox"""
        return await self.customer_dao.get_by_customer_id(customer_id)

    async def get_provider_inbox(self, provider_id: int):
        """GetProviderInbox"""
        return await self.provider_dao.get_by_provider_id(provider_id)
