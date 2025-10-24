"""Tests for RatingDAO."""

from unittest.mock import AsyncMock

import pytest

from review_service.models.rating import ProviderRating


class TestRatingDAOGet:
    """Test RatingDAO get methods."""

    @pytest.mark.asyncio
    async def test_get_by_provider_id_success(self, rating_dao, mock_rating_collection):
        """Test successfully getting rating by provider ID."""
        mock_rating_collection.find_one = AsyncMock(
            return_value={"_id": "mongo_id", "provider_id": 2, "average_rating": 4.5, "total_reviews": 10}
        )

        rating = await rating_dao.get_by_provider_id(2)

        assert rating is not None
        assert rating.provider_id == 2
        assert rating.average_rating == 4.5
        assert rating.total_reviews == 10
        mock_rating_collection.find_one.assert_called_once_with({"provider_id": 2})

    @pytest.mark.asyncio
    async def test_get_by_provider_id_not_found(self, rating_dao, mock_rating_collection):
        """Test getting rating when provider doesn't exist."""
        mock_rating_collection.find_one = AsyncMock(return_value=None)

        rating = await rating_dao.get_by_provider_id(999)

        assert rating is None
        mock_rating_collection.find_one.assert_called_once_with({"provider_id": 999})

    @pytest.mark.asyncio
    async def test_get_by_provider_id_removes_mongodb_id(self, rating_dao, mock_rating_collection):
        """Test that MongoDB _id field is removed from results."""
        mock_rating_collection.find_one = AsyncMock(
            return_value={
                "_id": "mongo_id_should_be_removed",
                "provider_id": 2,
                "average_rating": 4.5,
                "total_reviews": 10,
            }
        )

        rating = await rating_dao.get_by_provider_id(2)

        assert rating is not None
        rating_dict = rating.model_dump()
        assert "_id" not in rating_dict


class TestRatingDAOUpsert:
    """Test RatingDAO upsert method."""

    @pytest.mark.asyncio
    async def test_upsert_rating_new(self, rating_dao, mock_rating_collection):
        """Test upserting a new rating."""
        mock_rating_collection.update_one = AsyncMock()

        rating = await rating_dao.upsert_rating(provider_id=2, average_rating=4.5, total_reviews=10)

        assert rating.provider_id == 2
        assert rating.average_rating == 4.5
        assert rating.total_reviews == 10
        mock_rating_collection.update_one.assert_called_once_with(
            {"provider_id": 2}, {"$set": {"average_rating": 4.5, "total_reviews": 10}}, upsert=True
        )

    @pytest.mark.asyncio
    async def test_upsert_rating_update_existing(self, rating_dao, mock_rating_collection):
        """Test updating an existing rating."""
        mock_rating_collection.update_one = AsyncMock()

        rating = await rating_dao.upsert_rating(provider_id=2, average_rating=4.8, total_reviews=20)

        assert rating.provider_id == 2
        assert rating.average_rating == 4.8
        assert rating.total_reviews == 20
        mock_rating_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_rating_with_perfect_score(self, rating_dao, mock_rating_collection):
        """Test upserting with perfect 5.0 rating."""
        mock_rating_collection.update_one = AsyncMock()

        rating = await rating_dao.upsert_rating(provider_id=2, average_rating=5.0, total_reviews=5)

        assert rating.average_rating == 5.0
        assert rating.total_reviews == 5

    @pytest.mark.asyncio
    async def test_upsert_rating_with_low_score(self, rating_dao, mock_rating_collection):
        """Test upserting with low rating."""
        mock_rating_collection.update_one = AsyncMock()

        rating = await rating_dao.upsert_rating(provider_id=2, average_rating=2.5, total_reviews=2)

        assert rating.average_rating == 2.5
        assert rating.total_reviews == 2

    @pytest.mark.asyncio
    async def test_upsert_rating_incremental_update(self, rating_dao, mock_rating_collection):
        """Test incrementally updating rating after new review."""
        mock_rating_collection.update_one = AsyncMock()

        # First review: 5 stars
        rating1 = await rating_dao.upsert_rating(provider_id=2, average_rating=5.0, total_reviews=1)
        assert rating1.average_rating == 5.0
        assert rating1.total_reviews == 1

        # Second review: average becomes 4.5
        rating2 = await rating_dao.upsert_rating(provider_id=2, average_rating=4.5, total_reviews=2)
        assert rating2.average_rating == 4.5
        assert rating2.total_reviews == 2

        assert mock_rating_collection.update_one.call_count == 2
