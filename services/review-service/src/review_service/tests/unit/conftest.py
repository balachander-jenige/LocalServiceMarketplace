"""
Pytest fixtures for Review Service unit tests.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

from review_service.dao.rating_dao import RatingDAO
from review_service.dao.review_dao import ReviewDAO
from review_service.services.review_service import ReviewService


@pytest.fixture
def mock_db():
    """Mock MongoDB database."""
    db = MagicMock(spec=AsyncIOMotorDatabase)
    db.__getitem__ = MagicMock()
    return db


@pytest.fixture
def mock_review_collection():
    """Mock review collection."""
    collection = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.find = MagicMock()
    return collection


@pytest.fixture
def mock_rating_collection():
    """Mock rating collection."""
    collection = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    return collection


@pytest.fixture
def review_dao(mock_db, mock_review_collection):
    """Create ReviewDAO with mocked database."""
    mock_db.__getitem__.return_value = mock_review_collection
    return ReviewDAO(mock_db)


@pytest.fixture
def rating_dao(mock_db, mock_rating_collection):
    """Create RatingDAO with mocked database."""
    mock_db.__getitem__.return_value = mock_rating_collection
    return RatingDAO(mock_db)


@pytest.fixture
def review_service(mock_db):
    """Create ReviewService with mocked database."""
    return ReviewService(mock_db)


@pytest.fixture
def sample_review():
    """Sample review data."""
    return {
        "order_id": 100,
        "customer_id": 1,
        "provider_id": 2,
        "stars": 5,
        "content": "Excellent service!",
        "created_at": datetime(2025, 10, 24, 12, 0, 0),
    }


@pytest.fixture
def sample_rating():
    """Sample rating data."""
    return {"provider_id": 2, "average_rating": 4.5, "total_reviews": 10}


@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher."""
    mock_publish_review_created = mocker.patch(
        "review_service.services.review_service.EventPublisher.publish_review_created", new_callable=AsyncMock
    )
    mock_publish_rating_updated = mocker.patch(
        "review_service.services.review_service.EventPublisher.publish_rating_updated", new_callable=AsyncMock
    )
    return {
        "publish_review_created": mock_publish_review_created,
        "publish_rating_updated": mock_publish_rating_updated,
    }
    """Mock EventPublisher."""
    return mocker.patch("review_service.services.review_service.EventPublisher")
