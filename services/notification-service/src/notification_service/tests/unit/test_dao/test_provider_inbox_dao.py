"""Tests for ProviderInboxDAO."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from notification_service.models.provider_inbox import ProviderInbox


class TestProviderInboxDAOCreate:
    """Test ProviderInboxDAO create method."""

    @pytest.mark.asyncio
    async def test_create_success(self, provider_dao, mock_provider_collection, sample_provider_notification):
        """Test successfully creating a provider notification."""
        notification = ProviderInbox(**sample_provider_notification)
        mock_provider_collection.insert_one = AsyncMock()

        result = await provider_dao.create(notification)

        assert result == notification
        mock_provider_collection.insert_one.assert_called_once()
        call_args = mock_provider_collection.insert_one.call_args[0][0]
        assert call_args["provider_id"] == 2
        assert call_args["order_id"] == 100
        assert call_args["message"] == "You have accepted an order"

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, provider_dao, mock_provider_collection):
        """Test creating notification with all fields."""
        notification = ProviderInbox(
            provider_id=10,
            order_id=300,
            message="Payment received",
            created_at=datetime(2025, 10, 24, 15, 30, 0),
            is_read=True,
        )
        mock_provider_collection.insert_one = AsyncMock()

        result = await provider_dao.create(notification)

        assert result.provider_id == 10
        assert result.order_id == 300
        assert result.message == "Payment received"
        assert result.is_read is True
        mock_provider_collection.insert_one.assert_called_once()


class TestProviderInboxDAOGet:
    """Test ProviderInboxDAO get methods."""

    @pytest.mark.asyncio
    async def test_get_by_provider_id_success(self, provider_dao, mock_provider_collection):
        """Test successfully getting provider notifications."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "_id": "mongo_id_1",
                    "provider_id": 2,
                    "order_id": 100,
                    "message": "Order accepted",
                    "created_at": datetime(2025, 10, 24, 12, 0, 0),
                    "is_read": False,
                },
                {
                    "_id": "mongo_id_2",
                    "provider_id": 2,
                    "order_id": 101,
                    "message": "Payment received",
                    "created_at": datetime(2025, 10, 24, 13, 0, 0),
                    "is_read": True,
                },
            ]
        )
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_provider_collection.find = MagicMock(return_value=mock_cursor)

        notifications = await provider_dao.get_by_provider_id(2)

        assert len(notifications) == 2
        assert notifications[0].provider_id == 2
        assert notifications[0].order_id == 100
        assert notifications[0].is_read is False
        assert notifications[1].order_id == 101
        assert notifications[1].is_read is True
        mock_provider_collection.find.assert_called_once_with({"provider_id": 2})
        mock_cursor.sort.assert_called_once_with("created_at", -1)

    @pytest.mark.asyncio
    async def test_get_by_provider_id_empty(self, provider_dao, mock_provider_collection):
        """Test getting notifications for provider with no notifications."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_provider_collection.find = MagicMock(return_value=mock_cursor)

        notifications = await provider_dao.get_by_provider_id(999)

        assert len(notifications) == 0
        mock_provider_collection.find.assert_called_once_with({"provider_id": 999})

    @pytest.mark.asyncio
    async def test_get_removes_mongodb_id(self, provider_dao, mock_provider_collection):
        """Test that MongoDB _id field is removed from results."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "_id": "mongo_id_should_be_removed",
                    "provider_id": 2,
                    "order_id": 100,
                    "message": "Test message",
                    "created_at": datetime(2025, 10, 24, 12, 0, 0),
                    "is_read": False,
                }
            ]
        )
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_provider_collection.find = MagicMock(return_value=mock_cursor)

        notifications = await provider_dao.get_by_provider_id(2)

        assert len(notifications) == 1
        # Verify _id is not in the model
        notification_dict = notifications[0].model_dump()
        assert "_id" not in notification_dict


class TestProviderInboxDAOMarkAsRead:
    """Test ProviderInboxDAO mark_as_read method."""

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, provider_dao, mock_provider_collection):
        """Test successfully marking notifications as read."""
        mock_provider_collection.update_many = AsyncMock()

        await provider_dao.mark_as_read(provider_id=2, order_id=100)

        mock_provider_collection.update_many.assert_called_once_with(
            {"provider_id": 2, "order_id": 100}, {"$set": {"is_read": True}}
        )

    @pytest.mark.asyncio
    async def test_mark_as_read_multiple_notifications(self, provider_dao, mock_provider_collection):
        """Test marking multiple notifications as read for same order."""
        mock_provider_collection.update_many = AsyncMock(return_value=MagicMock(modified_count=3))

        await provider_dao.mark_as_read(provider_id=2, order_id=100)

        mock_provider_collection.update_many.assert_called_once()
        call_args = mock_provider_collection.update_many.call_args
        assert call_args[0][0] == {"provider_id": 2, "order_id": 100}
        assert call_args[0][1] == {"$set": {"is_read": True}}

    @pytest.mark.asyncio
    async def test_mark_as_read_no_matching_notifications(self, provider_dao, mock_provider_collection):
        """Test marking as read when no notifications match."""
        mock_provider_collection.update_many = AsyncMock(return_value=MagicMock(modified_count=0))

        await provider_dao.mark_as_read(provider_id=999, order_id=999)

        mock_provider_collection.update_many.assert_called_once_with(
            {"provider_id": 999, "order_id": 999}, {"$set": {"is_read": True}}
        )
