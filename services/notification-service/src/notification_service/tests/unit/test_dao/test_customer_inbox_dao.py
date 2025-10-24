"""Tests for CustomerInboxDAO."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from notification_service.models.customer_inbox import CustomerInbox


class TestCustomerInboxDAOCreate:
    """Test CustomerInboxDAO create method."""

    @pytest.mark.asyncio
    async def test_create_success(self, customer_dao, mock_customer_collection, sample_customer_notification):
        """Test successfully creating a customer notification."""
        notification = CustomerInbox(**sample_customer_notification)
        mock_customer_collection.insert_one = AsyncMock()

        result = await customer_dao.create(notification)

        assert result == notification
        mock_customer_collection.insert_one.assert_called_once()
        call_args = mock_customer_collection.insert_one.call_args[0][0]
        assert call_args["customer_id"] == 1
        assert call_args["order_id"] == 100
        assert call_args["message"] == "Your order has been accepted"

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, customer_dao, mock_customer_collection):
        """Test creating notification with all fields."""
        notification = CustomerInbox(
            customer_id=5,
            order_id=200,
            message="Order completed",
            created_at=datetime(2025, 10, 24, 14, 30, 0),
            is_read=True,
        )
        mock_customer_collection.insert_one = AsyncMock()

        result = await customer_dao.create(notification)

        assert result.customer_id == 5
        assert result.order_id == 200
        assert result.message == "Order completed"
        assert result.is_read is True
        mock_customer_collection.insert_one.assert_called_once()


class TestCustomerInboxDAOGet:
    """Test CustomerInboxDAO get methods."""

    @pytest.mark.asyncio
    async def test_get_by_customer_id_success(self, customer_dao, mock_customer_collection):
        """Test successfully getting customer notifications."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "_id": "mongo_id_1",
                    "customer_id": 1,
                    "order_id": 100,
                    "message": "Order accepted",
                    "created_at": datetime(2025, 10, 24, 12, 0, 0),
                    "is_read": False,
                },
                {
                    "_id": "mongo_id_2",
                    "customer_id": 1,
                    "order_id": 101,
                    "message": "Order completed",
                    "created_at": datetime(2025, 10, 24, 13, 0, 0),
                    "is_read": True,
                },
            ]
        )
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_customer_collection.find = MagicMock(return_value=mock_cursor)

        notifications = await customer_dao.get_by_customer_id(1)

        assert len(notifications) == 2
        assert notifications[0].customer_id == 1
        assert notifications[0].order_id == 100
        assert notifications[0].is_read is False
        assert notifications[1].order_id == 101
        assert notifications[1].is_read is True
        mock_customer_collection.find.assert_called_once_with({"customer_id": 1})
        mock_cursor.sort.assert_called_once_with("created_at", -1)

    @pytest.mark.asyncio
    async def test_get_by_customer_id_empty(self, customer_dao, mock_customer_collection):
        """Test getting notifications for customer with no notifications."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_customer_collection.find = MagicMock(return_value=mock_cursor)

        notifications = await customer_dao.get_by_customer_id(999)

        assert len(notifications) == 0
        mock_customer_collection.find.assert_called_once_with({"customer_id": 999})

    @pytest.mark.asyncio
    async def test_get_removes_mongodb_id(self, customer_dao, mock_customer_collection):
        """Test that MongoDB _id field is removed from results."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "_id": "mongo_id_should_be_removed",
                    "customer_id": 1,
                    "order_id": 100,
                    "message": "Test message",
                    "created_at": datetime(2025, 10, 24, 12, 0, 0),
                    "is_read": False,
                }
            ]
        )
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_customer_collection.find = MagicMock(return_value=mock_cursor)

        notifications = await customer_dao.get_by_customer_id(1)

        assert len(notifications) == 1
        # Verify _id is not in the model
        notification_dict = notifications[0].model_dump()
        assert "_id" not in notification_dict


class TestCustomerInboxDAOMarkAsRead:
    """Test CustomerInboxDAO mark_as_read method."""

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, customer_dao, mock_customer_collection):
        """Test successfully marking notifications as read."""
        mock_customer_collection.update_many = AsyncMock()

        await customer_dao.mark_as_read(customer_id=1, order_id=100)

        mock_customer_collection.update_many.assert_called_once_with(
            {"customer_id": 1, "order_id": 100}, {"$set": {"is_read": True}}
        )

    @pytest.mark.asyncio
    async def test_mark_as_read_multiple_notifications(self, customer_dao, mock_customer_collection):
        """Test marking multiple notifications as read for same order."""
        mock_customer_collection.update_many = AsyncMock(return_value=MagicMock(modified_count=3))

        await customer_dao.mark_as_read(customer_id=1, order_id=100)

        mock_customer_collection.update_many.assert_called_once()
        call_args = mock_customer_collection.update_many.call_args
        assert call_args[0][0] == {"customer_id": 1, "order_id": 100}
        assert call_args[0][1] == {"$set": {"is_read": True}}

    @pytest.mark.asyncio
    async def test_mark_as_read_no_matching_notifications(self, customer_dao, mock_customer_collection):
        """Test marking as read when no notifications match."""
        mock_customer_collection.update_many = AsyncMock(return_value=MagicMock(modified_count=0))

        await customer_dao.mark_as_read(customer_id=999, order_id=999)

        mock_customer_collection.update_many.assert_called_once_with(
            {"customer_id": 999, "order_id": 999}, {"$set": {"is_read": True}}
        )
