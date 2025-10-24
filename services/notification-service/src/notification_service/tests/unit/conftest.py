"""
Pytest fixtures for Notification Service unit tests.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

from notification_service.dao.customer_inbox_dao import CustomerInboxDAO
from notification_service.dao.provider_inbox_dao import ProviderInboxDAO
from notification_service.services.notification_service import NotificationService


@pytest.fixture
def mock_db():
    """Mock MongoDB database."""
    db = MagicMock(spec=AsyncIOMotorDatabase)
    db.__getitem__ = MagicMock()
    return db


@pytest.fixture
def mock_customer_collection():
    """Mock customer inbox collection."""
    collection = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.find = MagicMock()
    collection.update_many = AsyncMock()
    return collection


@pytest.fixture
def mock_provider_collection():
    """Mock provider inbox collection."""
    collection = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.find = MagicMock()
    collection.update_many = AsyncMock()
    return collection


@pytest.fixture
def customer_dao(mock_db, mock_customer_collection):
    """Create CustomerInboxDAO with mocked database."""
    mock_db.__getitem__.return_value = mock_customer_collection
    return CustomerInboxDAO(mock_db)


@pytest.fixture
def provider_dao(mock_db, mock_provider_collection):
    """Create ProviderInboxDAO with mocked database."""
    mock_db.__getitem__.return_value = mock_provider_collection
    return ProviderInboxDAO(mock_db)


@pytest.fixture
def notification_service(mock_db):
    """Create NotificationService with mocked database."""
    return NotificationService(mock_db)


@pytest.fixture
def sample_customer_notification():
    """Sample customer notification data."""
    return {
        "customer_id": 1,
        "order_id": 100,
        "message": "Your order has been accepted",
        "created_at": datetime(2025, 10, 24, 12, 0, 0),
        "is_read": False,
    }


@pytest.fixture
def sample_provider_notification():
    """Sample provider notification data."""
    return {
        "provider_id": 2,
        "order_id": 100,
        "message": "You have accepted an order",
        "created_at": datetime(2025, 10, 24, 12, 0, 0),
        "is_read": False,
    }


@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher."""
    return mocker.patch("notification_service.services.notification_service.EventPublisher")
