"""Pytest configuration and fixtures for Order Service tests."""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.dao.order_dao import OrderDAO
from order_service.models.order import Order, OrderStatus, PaymentStatus, ServiceType, LocationEnum
from order_service.services.customer_order_service import CustomerOrderService
from order_service.services.provider_order_service import ProviderOrderService
from order_service.services.admin_order_service import AdminOrderService


@pytest.fixture
def mock_db(mocker):
    """Mock AsyncSession database."""
    db = mocker.MagicMock(spec=AsyncSession)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.get = AsyncMock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def sample_order():
    """Sample order data for testing."""
    return Order(
        id=1,
        customer_id=10,
        provider_id=None,
        title="Home Cleaning Service",
        description="Need deep cleaning for 2-bedroom apartment",
        service_type=ServiceType.CLEANING_REPAIR,
        status=OrderStatus.pending_review,
        price=150.00,
        location=LocationEnum.NORTH,
        address="123 Main St, Building A",
        service_start_time=datetime(2024, 1, 20, 10, 0),
        service_end_time=datetime(2024, 1, 20, 14, 0),
        payment_status=PaymentStatus.unpaid,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_pending_order():
    """Sample pending order (approved by admin)."""
    return Order(
        id=2,
        customer_id=10,
        provider_id=None,
        title="Web Development",
        description="Build a simple website",
        service_type=ServiceType.IT_TECHNOLOGY,
        status=OrderStatus.pending,
        price=500.00,
        location=LocationEnum.MID,
        address=None,
        service_start_time=None,
        service_end_time=None,
        payment_status=PaymentStatus.unpaid,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_accepted_order():
    """Sample accepted order with provider."""
    return Order(
        id=3,
        customer_id=10,
        provider_id=20,
        title="Math Tutoring",
        description="Need help with calculus",
        service_type=ServiceType.EDUCATION_TRAINING,
        status=OrderStatus.accepted,
        price=80.00,
        location=LocationEnum.EAST,
        address="456 School Rd",
        service_start_time=datetime(2024, 1, 22, 15, 0),
        service_end_time=datetime(2024, 1, 22, 17, 0),
        payment_status=PaymentStatus.unpaid,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher for testing event publishing."""
    mock_order_created = mocker.patch(
        "order_service.services.customer_order_service.EventPublisher.publish_order_created", new_callable=AsyncMock
    )
    mock_order_cancelled = mocker.patch(
        "order_service.services.customer_order_service.EventPublisher.publish_order_cancelled", new_callable=AsyncMock
    )
    mock_order_accepted = mocker.patch(
        "order_service.services.provider_order_service.EventPublisher.publish_order_accepted", new_callable=AsyncMock
    )
    mock_order_status_changed = mocker.patch(
        "order_service.services.provider_order_service.EventPublisher.publish_order_status_changed", new_callable=AsyncMock
    )
    mock_order_approved = mocker.patch(
        "order_service.services.admin_order_service.EventPublisher.publish_order_approved", new_callable=AsyncMock
    )
    mock_order_rejected = mocker.patch(
        "order_service.services.admin_order_service.EventPublisher.publish_order_rejected", new_callable=AsyncMock
    )

    return {
        "order_created": mock_order_created,
        "order_cancelled": mock_order_cancelled,
        "order_accepted": mock_order_accepted,
        "order_status_changed": mock_order_status_changed,
        "order_approved": mock_order_approved,
        "order_rejected": mock_order_rejected,
    }


@pytest.fixture
def customer_order_service():
    """Create CustomerOrderService instance."""
    return CustomerOrderService()


@pytest.fixture
def provider_order_service():
    """Create ProviderOrderService instance."""
    return ProviderOrderService()


@pytest.fixture
def admin_order_service():
    """Create AdminOrderService instance."""
    return AdminOrderService()
