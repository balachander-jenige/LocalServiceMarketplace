"""Tests for ReviewService."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from review_service.models.rating import ProviderRating
from review_service.models.review import Review


class TestReviewServiceCreateReview:
    """Test ReviewService.create_review method."""

    @pytest.mark.asyncio
    async def test_create_review_success(self, review_service, mock_event_publisher):
        """Test successfully creating a review."""
        # Arrange
        review_service.review_dao.create = AsyncMock(
            return_value=Review(
                order_id=100,
                customer_id=1,
                provider_id=2,
                stars=5,
                content="Excellent service!",
                created_at=datetime.now(),
            )
        )
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[
                Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now()),
                Review(order_id=101, customer_id=2, provider_id=2, stars=4, created_at=datetime.now()),
            ]
        )
        review_service.rating_dao.upsert_rating = AsyncMock(
            return_value=ProviderRating(provider_id=2, average_rating=4.5, total_reviews=2)
        )

        # Act
        review_data = {
            "order_id": 100,
            "customer_id": 1,
            "provider_id": 2,
            "stars": 5,
            "content": "Excellent service!",
        }
        review = await review_service.create_review(review_data)

        # Assert
        assert review.order_id == 100
        assert review.stars == 5
        assert review.content == "Excellent service!"
        review_service.review_dao.create.assert_called_once()
        review_service.rating_dao.upsert_rating.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_review_without_content(self, review_service, mock_event_publisher):
        """Test creating a review without optional content."""
        # Arrange
        review_service.review_dao.create = AsyncMock(
            return_value=Review(
                order_id=100, customer_id=1, provider_id=2, stars=4, content=None, created_at=datetime.now()
            )
        )
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[Review(order_id=100, customer_id=1, provider_id=2, stars=4, created_at=datetime.now())]
        )
        review_service.rating_dao.upsert_rating = AsyncMock(
            return_value=ProviderRating(provider_id=2, average_rating=4.0, total_reviews=1)
        )

        # Act
        review_data = {"order_id": 100, "customer_id": 1, "provider_id": 2, "stars": 4}
        review = await review_service.create_review(review_data)

        # Assert
        assert review.order_id == 100
        assert review.stars == 4
        assert review.content is None
        review_service.review_dao.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_review_publishes_review_created_event(self, review_service, mock_event_publisher):
        """Test that ReviewCreatedEvent is published."""
        # Arrange
        review_service.review_dao.create = AsyncMock(
            return_value=Review(
                order_id=100, customer_id=1, provider_id=2, stars=5, content="Great!", created_at=datetime.now()
            )
        )
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now())]
        )
        review_service.rating_dao.upsert_rating = AsyncMock(
            return_value=ProviderRating(provider_id=2, average_rating=5.0, total_reviews=1)
        )

        # Act
        review_data = {"order_id": 100, "customer_id": 1, "provider_id": 2, "stars": 5, "content": "Great!"}
        await review_service.create_review(review_data)

        # Assert
        mock_event_publisher["publish_review_created"].assert_called_once()
        mock_event_publisher["publish_rating_updated"].assert_called_once()

    @pytest.mark.asyncio
    async def test_create_review_publishes_rating_updated_event(self, review_service, mock_event_publisher):
        """Test that RatingUpdatedEvent is published."""
        # Arrange
        review_service.review_dao.create = AsyncMock(
            return_value=Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now())
        )
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now())]
        )
        review_service.rating_dao.upsert_rating = AsyncMock(
            return_value=ProviderRating(provider_id=2, average_rating=5.0, total_reviews=1)
        )

        # Act
        review_data = {"order_id": 100, "customer_id": 1, "provider_id": 2, "stars": 5}
        await review_service.create_review(review_data)

        # Assert
        mock_event_publisher["publish_rating_updated"].assert_called_once()

    @pytest.mark.asyncio
    async def test_create_review_calculates_average_rating(self, review_service, mock_event_publisher):
        """Test that average rating is calculated correctly."""
        # Arrange
        review_service.review_dao.create = AsyncMock(
            return_value=Review(order_id=102, customer_id=3, provider_id=2, stars=3, created_at=datetime.now())
        )
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[
                Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now()),
                Review(order_id=101, customer_id=2, provider_id=2, stars=4, created_at=datetime.now()),
                Review(order_id=102, customer_id=3, provider_id=2, stars=3, created_at=datetime.now()),
            ]
        )
        review_service.rating_dao.upsert_rating = AsyncMock()

        # Act
        review_data = {"order_id": 102, "customer_id": 3, "provider_id": 2, "stars": 3}
        await review_service.create_review(review_data)

        # Assert
        review_service.rating_dao.upsert_rating.assert_called_once()
        # The upsert_rating is called with positional arguments
        call_args = review_service.rating_dao.upsert_rating.call_args[0]
        assert call_args[0] == 2  # provider_id
        assert call_args[1] == 4.0  # average_rating: (5 + 4 + 3) / 3 = 4.0
        assert call_args[2] == 3  # total_reviews

    @pytest.mark.asyncio
    async def test_create_review_updates_rating_in_dao(self, review_service, mock_event_publisher):
        """Test that rating is updated via rating_dao.upsert_rating."""
        # Arrange
        review_service.review_dao.create = AsyncMock(
            return_value=Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now())
        )
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now())]
        )
        review_service.rating_dao.upsert_rating = AsyncMock(
            return_value=ProviderRating(provider_id=2, average_rating=5.0, total_reviews=1)
        )

        # Act
        review_data = {"order_id": 100, "customer_id": 1, "provider_id": 2, "stars": 5}
        await review_service.create_review(review_data)

        # Assert
        call_args = review_service.rating_dao.upsert_rating.call_args[0]
        assert call_args == (2, 5.0, 1)

    @pytest.mark.asyncio
    async def test_create_review_with_multiple_reviews(self, review_service, mock_event_publisher):
        """Test creating review when provider has multiple existing reviews."""
        # Arrange
        review_service.review_dao.create = AsyncMock(
            return_value=Review(order_id=105, customer_id=5, provider_id=2, stars=2, created_at=datetime.now())
        )
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[
                Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now()),
                Review(order_id=101, customer_id=2, provider_id=2, stars=4, created_at=datetime.now()),
                Review(order_id=102, customer_id=3, provider_id=2, stars=3, created_at=datetime.now()),
                Review(order_id=103, customer_id=4, provider_id=2, stars=5, created_at=datetime.now()),
                Review(order_id=105, customer_id=5, provider_id=2, stars=2, created_at=datetime.now()),
            ]
        )
        review_service.rating_dao.upsert_rating = AsyncMock()

        # Act
        review_data = {"order_id": 105, "customer_id": 5, "provider_id": 2, "stars": 2}
        await review_service.create_review(review_data)

        # Assert
        call_args = review_service.rating_dao.upsert_rating.call_args[0]
        assert call_args[1] == 3.8  # average_rating: (5+4+3+5+2)/5 = 3.8
        assert call_args[2] == 5  # total_reviews


class TestReviewServiceGetProviderRating:
    """Test ReviewService.get_provider_rating method."""

    @pytest.mark.asyncio
    async def test_get_provider_rating_success(self, review_service):
        """Test getting provider rating successfully."""
        review_service.rating_dao.get_by_provider_id = AsyncMock(
            return_value=ProviderRating(provider_id=2, average_rating=4.5, total_reviews=10)
        )

        rating = await review_service.get_provider_rating(2)

        assert rating.provider_id == 2
        assert rating.average_rating == 4.5
        assert rating.total_reviews == 10
        review_service.rating_dao.get_by_provider_id.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_get_provider_rating_returns_default_when_not_found(self, review_service):
        """Test that default rating is returned when provider has no rating."""
        review_service.rating_dao.get_by_provider_id = AsyncMock(return_value=None)

        rating = await review_service.get_provider_rating(999)

        assert rating.provider_id == 999
        assert rating.average_rating == 5.0  # Default value
        assert rating.total_reviews == 0
        review_service.rating_dao.get_by_provider_id.assert_called_once_with(999)


class TestReviewServiceGetReviewsForProvider:
    """Test ReviewService.get_reviews_for_provider method."""

    @pytest.mark.asyncio
    async def test_get_reviews_for_provider_success(self, review_service):
        """Test getting reviews for a provider."""
        review_service.review_dao.get_reviews_for_provider = AsyncMock(
            return_value=[
                Review(
                    order_id=100, customer_id=1, provider_id=2, stars=5, content="Great!", created_at=datetime.now()
                ),
                Review(
                    order_id=101, customer_id=2, provider_id=2, stars=4, content="Good", created_at=datetime.now()
                ),
            ]
        )

        reviews = await review_service.get_reviews_for_provider(2)

        assert len(reviews) == 2
        assert reviews[0].stars == 5
        assert reviews[1].stars == 4
        review_service.review_dao.get_reviews_for_provider.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_get_reviews_for_provider_empty(self, review_service):
        """Test getting reviews when provider has no reviews."""
        review_service.review_dao.get_reviews_for_provider = AsyncMock(return_value=[])

        reviews = await review_service.get_reviews_for_provider(999)

        assert reviews == []
        review_service.review_dao.get_reviews_for_provider.assert_called_once_with(999)


class TestReviewServiceGetReviewByOrder:
    """Test ReviewService.get_review_by_order method."""

    @pytest.mark.asyncio
    async def test_get_review_by_order_success(self, review_service):
        """Test getting review by order ID."""
        review_service.review_dao.get_by_order_id = AsyncMock(
            return_value=Review(
                order_id=100, customer_id=1, provider_id=2, stars=5, content="Excellent!", created_at=datetime.now()
            )
        )

        review = await review_service.get_review_by_order(100)

        assert review is not None
        assert review.order_id == 100
        assert review.stars == 5
        review_service.review_dao.get_by_order_id.assert_called_once_with(100)

    @pytest.mark.asyncio
    async def test_get_review_by_order_not_found(self, review_service):
        """Test getting review when order has no review."""
        review_service.review_dao.get_by_order_id = AsyncMock(return_value=None)

        review = await review_service.get_review_by_order(999)

        assert review is None
        review_service.review_dao.get_by_order_id.assert_called_once_with(999)
