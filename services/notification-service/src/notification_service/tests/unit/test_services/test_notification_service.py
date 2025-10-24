"""Tests for NotificationService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from notification_service.models.customer_inbox import CustomerInbox
from notification_service.models.provider_inbox import ProviderInbox


class TestNotificationServiceSendCustomer:
    """Test NotificationService send_customer_notification method."""

    @pytest.mark.asyncio
    async def test_send_customer_notification_success(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test successfully sending customer notification."""
        # Mock DAOs
        mock_customer_dao = mocker.patch.object(notification_service, "customer_dao")
        mock_customer_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        await notification_service.send_customer_notification(
            customer_id=1, order_id=100, message="Your order has been accepted"
        )

        # Verify DAO was called
        mock_customer_dao.create.assert_called_once()
        call_args = mock_customer_dao.create.call_args[0][0]
        assert isinstance(call_args, CustomerInbox)
        assert call_args.customer_id == 1
        assert call_args.order_id == 100
        assert call_args.message == "Your order has been accepted"
        assert call_args.is_read is False

        # Verify event was published
        mock_event_publisher.publish_notification_sent.assert_called_once()
        event_args = mock_event_publisher.publish_notification_sent.call_args[0][0]
        assert event_args.recipient_id == 1
        assert event_args.recipient_type == "customer"
        assert event_args.order_id == 100
        assert event_args.message == "Your order has been accepted"

    @pytest.mark.asyncio
    async def test_send_customer_notification_with_none_order_id(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test sending customer notification without order_id."""
        mock_customer_dao = mocker.patch.object(notification_service, "customer_dao")
        mock_customer_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        await notification_service.send_customer_notification(
            customer_id=1, order_id=None, message="System notification"
        )

        mock_customer_dao.create.assert_called_once()
        call_args = mock_customer_dao.create.call_args[0][0]
        assert call_args.order_id is None
        assert call_args.message == "System notification"

    @pytest.mark.asyncio
    async def test_send_customer_notification_creates_timestamp(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test that timestamp is created for notification."""
        mock_customer_dao = mocker.patch.object(notification_service, "customer_dao")
        mock_customer_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        before = datetime.utcnow()
        await notification_service.send_customer_notification(
            customer_id=1, order_id=100, message="Test message"
        )
        after = datetime.utcnow()

        call_args = mock_customer_dao.create.call_args[0][0]
        assert before <= call_args.created_at <= after

    @pytest.mark.asyncio
    async def test_send_customer_notification_publishes_event(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test that event is published after notification creation."""
        mock_customer_dao = mocker.patch.object(notification_service, "customer_dao")
        mock_customer_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        await notification_service.send_customer_notification(
            customer_id=5, order_id=200, message="Important notification"
        )

        # Verify both DAO and event publisher were called
        assert mock_customer_dao.create.called
        assert mock_event_publisher.publish_notification_sent.called

        # Verify event details
        event_args = mock_event_publisher.publish_notification_sent.call_args[0][0]
        assert event_args.recipient_id == 5
        assert event_args.recipient_type == "customer"


class TestNotificationServiceSendProvider:
    """Test NotificationService send_provider_notification method."""

    @pytest.mark.asyncio
    async def test_send_provider_notification_success(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test successfully sending provider notification."""
        # Mock DAOs
        mock_provider_dao = mocker.patch.object(notification_service, "provider_dao")
        mock_provider_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        await notification_service.send_provider_notification(
            provider_id=2, order_id=100, message="You have accepted an order"
        )

        # Verify DAO was called
        mock_provider_dao.create.assert_called_once()
        call_args = mock_provider_dao.create.call_args[0][0]
        assert isinstance(call_args, ProviderInbox)
        assert call_args.provider_id == 2
        assert call_args.order_id == 100
        assert call_args.message == "You have accepted an order"
        assert call_args.is_read is False

        # Verify event was published
        mock_event_publisher.publish_notification_sent.assert_called_once()
        event_args = mock_event_publisher.publish_notification_sent.call_args[0][0]
        assert event_args.recipient_id == 2
        assert event_args.recipient_type == "provider"
        assert event_args.order_id == 100
        assert event_args.message == "You have accepted an order"

    @pytest.mark.asyncio
    async def test_send_provider_notification_with_none_order_id(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test sending provider notification without order_id."""
        mock_provider_dao = mocker.patch.object(notification_service, "provider_dao")
        mock_provider_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        await notification_service.send_provider_notification(
            provider_id=2, order_id=None, message="System notification"
        )

        mock_provider_dao.create.assert_called_once()
        call_args = mock_provider_dao.create.call_args[0][0]
        assert call_args.order_id is None
        assert call_args.message == "System notification"

    @pytest.mark.asyncio
    async def test_send_provider_notification_creates_timestamp(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test that timestamp is created for notification."""
        mock_provider_dao = mocker.patch.object(notification_service, "provider_dao")
        mock_provider_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        before = datetime.utcnow()
        await notification_service.send_provider_notification(
            provider_id=2, order_id=100, message="Test message"
        )
        after = datetime.utcnow()

        call_args = mock_provider_dao.create.call_args[0][0]
        assert before <= call_args.created_at <= after

    @pytest.mark.asyncio
    async def test_send_provider_notification_publishes_event(
        self, notification_service, mock_db, mock_event_publisher, mocker
    ):
        """Test that event is published after notification creation."""
        mock_provider_dao = mocker.patch.object(notification_service, "provider_dao")
        mock_provider_dao.create = AsyncMock()
        mock_event_publisher.publish_notification_sent = AsyncMock()

        await notification_service.send_provider_notification(
            provider_id=10, order_id=300, message="Payment processed"
        )

        # Verify both DAO and event publisher were called
        assert mock_provider_dao.create.called
        assert mock_event_publisher.publish_notification_sent.called

        # Verify event details
        event_args = mock_event_publisher.publish_notification_sent.call_args[0][0]
        assert event_args.recipient_id == 10
        assert event_args.recipient_type == "provider"


class TestNotificationServiceGetInbox:
    """Test NotificationService get inbox methods."""

    @pytest.mark.asyncio
    async def test_get_customer_inbox_success(self, notification_service, mocker):
        """Test successfully getting customer inbox."""
        mock_customer_dao = mocker.patch.object(notification_service, "customer_dao")
        expected_notifications = [
            CustomerInbox(
                customer_id=1,
                order_id=100,
                message="Message 1",
                created_at=datetime(2025, 10, 24, 12, 0, 0),
                is_read=False,
            ),
            CustomerInbox(
                customer_id=1,
                order_id=101,
                message="Message 2",
                created_at=datetime(2025, 10, 24, 13, 0, 0),
                is_read=True,
            ),
        ]
        mock_customer_dao.get_by_customer_id = AsyncMock(return_value=expected_notifications)

        result = await notification_service.get_customer_inbox(customer_id=1)

        assert result == expected_notifications
        assert len(result) == 2
        mock_customer_dao.get_by_customer_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_customer_inbox_empty(self, notification_service, mocker):
        """Test getting empty customer inbox."""
        mock_customer_dao = mocker.patch.object(notification_service, "customer_dao")
        mock_customer_dao.get_by_customer_id = AsyncMock(return_value=[])

        result = await notification_service.get_customer_inbox(customer_id=999)

        assert result == []
        mock_customer_dao.get_by_customer_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_get_provider_inbox_success(self, notification_service, mocker):
        """Test successfully getting provider inbox."""
        mock_provider_dao = mocker.patch.object(notification_service, "provider_dao")
        expected_notifications = [
            ProviderInbox(
                provider_id=2,
                order_id=100,
                message="Message 1",
                created_at=datetime(2025, 10, 24, 12, 0, 0),
                is_read=False,
            ),
            ProviderInbox(
                provider_id=2,
                order_id=101,
                message="Message 2",
                created_at=datetime(2025, 10, 24, 13, 0, 0),
                is_read=True,
            ),
        ]
        mock_provider_dao.get_by_provider_id = AsyncMock(return_value=expected_notifications)

        result = await notification_service.get_provider_inbox(provider_id=2)

        assert result == expected_notifications
        assert len(result) == 2
        mock_provider_dao.get_by_provider_id.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_get_provider_inbox_empty(self, notification_service, mocker):
        """Test getting empty provider inbox."""
        mock_provider_dao = mocker.patch.object(notification_service, "provider_dao")
        mock_provider_dao.get_by_provider_id = AsyncMock(return_value=[])

        result = await notification_service.get_provider_inbox(provider_id=999)

        assert result == []
        mock_provider_dao.get_by_provider_id.assert_called_once_with(999)
