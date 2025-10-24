"""Tests for ReviewDAO."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from review_service.models.review import Review


class TestReviewDAOCreate:
    """Test ReviewDAO create method."""

    @pytest.mark.asyncio
    async def test_create_success(self, review_dao, mock_review_collection, sample_review):
        """Test successfully creating a review."""
        review = Review(**sample_review)
        mock_review_collection.insert_one = AsyncMock()

        result = await review_dao.create(review)

        assert result == review
        mock_review_collection.insert_one.assert_called_once()
        call_args = mock_review_collection.insert_one.call_args[0][0]
        assert call_args["order_id"] == 100
        assert call_args["customer_id"] == 1
        assert call_args["provider_id"] == 2
        assert call_args["stars"] == 5

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, review_dao, mock_review_collection):
        """Test creating review with all fields."""
        review = Review(
            order_id=200,
            customer_id=5,
            provider_id=10,
            stars=4,
            content="Good work",
            created_at=datetime(2025, 10, 24, 14, 30, 0),
        )
        mock_review_collection.insert_one = AsyncMock()

        result = await review_dao.create(review)

        assert result.order_id == 200
        assert result.customer_id == 5
        assert result.provider_id == 10
        assert result.stars == 4
        assert result.content == "Good work"
        mock_review_collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_without_content(self, review_dao, mock_review_collection):
        """Test creating review without optional content."""
        review = Review(order_id=300, customer_id=1, provider_id=2, stars=3, content=None)
        mock_review_collection.insert_one = AsyncMock()

        result = await review_dao.create(review)

        assert result.content is None
        mock_review_collection.insert_one.assert_called_once()


class TestReviewDAOGet:
    """Test ReviewDAO get methods."""

    @pytest.mark.asyncio
    async def test_get_by_order_id_success(self, review_dao, mock_review_collection):
        """Test successfully getting review by order ID."""
        mock_review_collection.find_one = AsyncMock(
            return_value={
                "_id": "mongo_id",
                "order_id": 100,
                "customer_id": 1,
                "provider_id": 2,
                "stars": 5,
                "content": "Excellent!",
                "created_at": datetime(2025, 10, 24, 12, 0, 0),
            }
        )

        review = await review_dao.get_by_order_id(100)

        assert review is not None
        assert review.order_id == 100
        assert review.customer_id == 1
        assert review.provider_id == 2
        assert review.stars == 5
        mock_review_collection.find_one.assert_called_once_with({"order_id": 100})

    @pytest.mark.asyncio
    async def test_get_by_order_id_not_found(self, review_dao, mock_review_collection):
        """Test getting review when order ID doesn't exist."""
        mock_review_collection.find_one = AsyncMock(return_value=None)

        review = await review_dao.get_by_order_id(999)

        assert review is None
        mock_review_collection.find_one.assert_called_once_with({"order_id": 999})

    @pytest.mark.asyncio
    async def test_get_by_order_id_removes_mongodb_id(self, review_dao, mock_review_collection):
        """Test that MongoDB _id field is removed from results."""
        mock_review_collection.find_one = AsyncMock(
            return_value={
                "_id": "mongo_id_should_be_removed",
                "order_id": 100,
                "customer_id": 1,
                "provider_id": 2,
                "stars": 5,
                "created_at": datetime(2025, 10, 24, 12, 0, 0),
            }
        )

        review = await review_dao.get_by_order_id(100)

        assert review is not None
        # Verify _id is not in the model
        review_dict = review.model_dump()
        assert "_id" not in review_dict

    @pytest.mark.asyncio
    async def test_get_reviews_for_provider_success(self, review_dao, mock_review_collection):
        """Test successfully getting all reviews for a provider."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "_id": "id1",
                    "order_id": 100,
                    "customer_id": 1,
                    "provider_id": 2,
                    "stars": 5,
                    "content": "Great!",
                    "created_at": datetime(2025, 10, 24, 12, 0, 0),
                },
                {
                    "_id": "id2",
                    "order_id": 101,
                    "customer_id": 3,
                    "provider_id": 2,
                    "stars": 4,
                    "content": "Good",
                    "created_at": datetime(2025, 10, 24, 13, 0, 0),
                },
            ]
        )
        mock_review_collection.find = MagicMock(return_value=mock_cursor)

        reviews = await review_dao.get_reviews_for_provider(2)

        assert len(reviews) == 2
        assert reviews[0].provider_id == 2
        assert reviews[0].stars == 5
        assert reviews[1].provider_id == 2
        assert reviews[1].stars == 4
        mock_review_collection.find.assert_called_once_with({"provider_id": 2})

    @pytest.mark.asyncio
    async def test_get_reviews_for_provider_empty(self, review_dao, mock_review_collection):
        """Test getting reviews for provider with no reviews."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_review_collection.find = MagicMock(return_value=mock_cursor)

        reviews = await review_dao.get_reviews_for_provider(999)

        assert len(reviews) == 0
        mock_review_collection.find.assert_called_once_with({"provider_id": 999})

    @pytest.mark.asyncio
    async def test_get_reviews_for_provider_removes_mongodb_ids(self, review_dao, mock_review_collection):
        """Test that MongoDB _id fields are removed from results."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "_id": "id1",
                    "order_id": 100,
                    "customer_id": 1,
                    "provider_id": 2,
                    "stars": 5,
                    "created_at": datetime(2025, 10, 24, 12, 0, 0),
                }
            ]
        )
        mock_review_collection.find = MagicMock(return_value=mock_cursor)

        reviews = await review_dao.get_reviews_for_provider(2)

        assert len(reviews) == 1
        review_dict = reviews[0].model_dump()
        assert "_id" not in review_dict
