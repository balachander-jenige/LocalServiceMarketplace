"""
单元测试通用Fixtures配置
提供Mock对象和测试数据
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_mongo_db():
    """Mock MongoDBDatabase"""
    mock_db = MagicMock()
    return mock_db


@pytest.fixture
def mock_customer_dao():
    """Mock CustomerProfileDAO"""
    dao = AsyncMock()
    dao.get_by_user_id = AsyncMock()
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    return dao


@pytest.fixture
def mock_provider_dao():
    """Mock ProviderProfileDAO"""
    dao = AsyncMock()
    dao.get_by_user_id = AsyncMock()
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    dao.search_providers = AsyncMock()
    return dao


@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher"""
    mocker.patch("user_service.services.customer_profile_service.EventPublisher.publish_profile_created")
    mocker.patch("user_service.services.customer_profile_service.EventPublisher.publish_profile_updated")
    mocker.patch("user_service.services.provider_profile_service.EventPublisher.publish_profile_created")
    mocker.patch("user_service.services.provider_profile_service.EventPublisher.publish_profile_updated")


@pytest.fixture
def sample_customer_profile():
    """StandardCustomerProfileTestData(ModelObject)"""
    from user_service.models.customer_profile import CustomerProfile

    return CustomerProfile(
        user_id=1,
        location="NORTH",
        address="123 Test St",
        budget_preference=100.0,
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 1),
    )


@pytest.fixture
def sample_provider_profile():
    """StandardProviderProfileTestData(ModelObject)"""
    from user_service.models.provider_profile import ProviderProfile

    return ProviderProfile(
        user_id=2,
        skills=["Python", "FastAPI"],
        experience_years=5,
        hourly_rate=50.0,
        availability="Full-time",
        portfolio=["project1", "project2"],
        rating=4.5,
        total_reviews=10,
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 1),
    )


@pytest.fixture
def sample_auth_user():
    """Auth ServiceReturn的UserData"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@test.com",
        "role_id": 1,
        "created_at": "2025-01-01T00:00:00",
    }


@pytest.fixture
def mock_httpx_client(mocker):
    """Mock httpx.AsyncClient"""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.put = AsyncMock(return_value=mock_response)

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_customer_profile_model():
    """Mock CustomerProfileObject"""
    from user_service.models.customer_profile import CustomerProfile, LocationEnum

    profile = CustomerProfile(
        user_id=1, location=LocationEnum.NORTH, address="123 Test St", budget_preference=100.0
    )
    return profile


@pytest.fixture
def mock_provider_profile_model():
    """Mock ProviderProfileObject"""
    from user_service.models.provider_profile import ProviderProfile

    profile = ProviderProfile(
        user_id=2,
        skills=["Python", "FastAPI"],
        experience_years=5,
        hourly_rate=50.0,
        availability="Full-time",
        portfolio=[],
        rating=4.5,
        total_reviews=10,
    )
    return profile
