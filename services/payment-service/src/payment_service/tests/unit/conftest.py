"""Shared test fixtures for payment service unit tests."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from payment_service.models.payment import Payment, PaymentMethod, PaymentStatus


@pytest.fixture
def mock_db():
    """Mock AsyncSession for database operations."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.get = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.delete = AsyncMock()
    return mock_session


@pytest.fixture
def sample_payment():
    """Sample payment in pending status."""
    return Payment(
        id=1,
        order_id=100,
        customer_id=10,
        provider_id=20,
        amount=150.00,
        payment_method=PaymentMethod.simulated,
        status=PaymentStatus.pending,
        transaction_id="test-txn-001",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_completed_payment():
    """Sample payment in completed status."""
    return Payment(
        id=2,
        order_id=101,
        customer_id=10,
        provider_id=20,
        amount=200.00,
        payment_method=PaymentMethod.simulated,
        status=PaymentStatus.completed,
        transaction_id="test-txn-002",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_failed_payment():
    """Sample payment in failed status."""
    return Payment(
        id=3,
        order_id=102,
        customer_id=10,
        provider_id=20,
        amount=100.00,
        payment_method=PaymentMethod.simulated,
        status=PaymentStatus.failed,
        transaction_id="test-txn-003",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher for testing event publishing."""
    mock_payment_initiated = mocker.patch(
        "payment_service.services.payment_service.EventPublisher.publish_payment_initiated", new_callable=AsyncMock
    )
    mock_payment_completed = mocker.patch(
        "payment_service.services.payment_service.EventPublisher.publish_payment_completed", new_callable=AsyncMock
    )

    return {
        "payment_initiated": mock_payment_initiated,
        "payment_completed": mock_payment_completed,
    }


@pytest.fixture
def mock_httpx_client(monkeypatch):
    """Mock httpx AsyncClient for external API calls."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    
    # Create a proper async context manager mock
    async def async_enter(*args, **kwargs):
        return mock_client
    
    async def async_exit(*args, **kwargs):
        return None
    
    mock_context = MagicMock()
    mock_context.__aenter__ = async_enter
    mock_context.__aexit__ = async_exit
    
    # Patch httpx.AsyncClient to return our context manager
    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: mock_context)
    
    return mock_client
