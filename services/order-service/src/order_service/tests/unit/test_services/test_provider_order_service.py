"""
Unit tests for ProviderOrderService.

Tests cover provider order operations including:
- Viewing available orders
- Accepting orders
- Updating order status (start, complete)
- Getting order history and details
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from order_service.dao.order_dao import OrderDAO
from order_service.models.order import LocationEnum, Order, OrderStatus, PaymentStatus, ServiceType
from order_service.services.provider_order_service import ProviderOrderService


class TestProviderOrderServiceListAvailableOrders:
    """Test listing available orders."""

    @pytest.mark.asyncio
    async def test_list_available_orders_success(self, mock_db):
        """Test successfully listing available orders."""
        # Arrange
        available_orders = [
            Order(
                id=1,
                customer_id=10,
                title="Test Order 1",
                description="Test description",
                service_type=ServiceType.CLEANING_REPAIR,
                status=OrderStatus.pending,
                price=100.00,
                location=LocationEnum.NORTH,
                address="123 Test St",
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Order(
                id=2,
                customer_id=11,
                title="Test Order 2",
                description="Test description 2",
                service_type=ServiceType.IT_TECHNOLOGY,
                status=OrderStatus.pending,
                price=200.00,
                location=LocationEnum.SOUTH,
                address="456 Test Ave",
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

        with patch.object(OrderDAO, "get_available_orders", new_callable=AsyncMock, return_value=available_orders):
            # Act
            result = await ProviderOrderService.list_available_orders(db=mock_db, location="NORTH")

            # Assert
            assert len(result) == 2
            assert result[0].id == 1
            assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_list_available_orders_with_filters(self, mock_db):
        """Test listing available orders with service type filter."""
        # Arrange
        filtered_orders = [
            Order(
                id=1,
                customer_id=10,
                title="Education Order",
                description="Test description",
                service_type=ServiceType.EDUCATION_TRAINING,
                status=OrderStatus.pending,
                price=150.00,
                location=LocationEnum.NORTH,
                address="123 Test St",
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

        with patch.object(OrderDAO, "get_available_orders", new_callable=AsyncMock, return_value=filtered_orders):
            # Act
            result = await ProviderOrderService.list_available_orders(
                db=mock_db, location="NORTH", service_type="education_training", min_price=100.0
            )

            # Assert
            assert len(result) == 1
            assert result[0].service_type == ServiceType.EDUCATION_TRAINING


class TestProviderOrderServiceGetAvailableOrderDetail:
    """Test getting available order details."""

    @pytest.mark.asyncio
    async def test_get_available_order_detail_success(self, mock_db, sample_pending_order):
        """Test successfully getting available order detail."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_pending_order):
            # Act
            result = await ProviderOrderService.get_available_order_detail(db=mock_db, order_id=1)

            # Assert
            assert result.id == sample_pending_order.id
            assert result.status == OrderStatus.pending

    @pytest.mark.asyncio
    async def test_get_available_order_detail_not_found(self, mock_db):
        """Test getting non-existent order."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.get_available_order_detail(db=mock_db, order_id=999)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_available_order_detail_not_pending(self, mock_db, sample_accepted_order):
        """Test getting order that is not available (not pending status)."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_accepted_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.get_available_order_detail(db=mock_db, order_id=1)

            assert exc_info.value.status_code == 400
            assert "no longer available" in exc_info.value.detail.lower()


class TestProviderOrderServiceAcceptOrder:
    """Test accepting orders."""

    @pytest.mark.asyncio
    async def test_accept_order_success(self, mock_db, sample_pending_order, mock_event_publisher):
        """Test successfully accepting an order."""
        # Arrange
        accepted_order = Order(
            id=sample_pending_order.id,
            customer_id=sample_pending_order.customer_id,
            provider_id=20,
            title=sample_pending_order.title,
            description=sample_pending_order.description,
            service_type=sample_pending_order.service_type,
            status=OrderStatus.accepted,
            price=sample_pending_order.price,
            location=sample_pending_order.location,
            address=sample_pending_order.address,
            payment_status=sample_pending_order.payment_status,
            created_at=sample_pending_order.created_at,
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_pending_order):
            with patch.object(OrderDAO, "accept_order", new_callable=AsyncMock, return_value=accepted_order):
                # Act
                result = await ProviderOrderService.accept_order(db=mock_db, provider_id=20, order_id=1)

                # Assert
                assert result.status == OrderStatus.accepted
                assert result.provider_id == 20
                mock_event_publisher["order_accepted"].assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_order_not_found(self, mock_db):
        """Test accepting non-existent order."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.accept_order(db=mock_db, provider_id=20, order_id=999)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_accept_order_already_accepted(self, mock_db, sample_accepted_order):
        """Test accepting order that is already accepted."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_accepted_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.accept_order(db=mock_db, provider_id=20, order_id=1)

            assert exc_info.value.status_code == 400
            assert "already been accepted" in exc_info.value.detail.lower()


class TestProviderOrderServiceUpdateOrderStatus:
    """Test updating order status."""

    @pytest.mark.asyncio
    async def test_update_order_status_to_in_progress(self, mock_db, sample_accepted_order, mock_event_publisher):
        """Test updating order status to in_progress."""
        # Arrange
        in_progress_order = Order(
            id=sample_accepted_order.id,
            customer_id=sample_accepted_order.customer_id,
            provider_id=sample_accepted_order.provider_id,
            title=sample_accepted_order.title,
            description=sample_accepted_order.description,
            service_type=sample_accepted_order.service_type,
            status=OrderStatus.in_progress,
            price=sample_accepted_order.price,
            location=sample_accepted_order.location,
            address=sample_accepted_order.address,
            payment_status=sample_accepted_order.payment_status,
            created_at=sample_accepted_order.created_at,
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_accepted_order):
            with patch.object(OrderDAO, "update_order_status", new_callable=AsyncMock, return_value=in_progress_order):
                # Act
                result = await ProviderOrderService.update_order_status(
                    db=mock_db, provider_id=20, order_id=1, new_status="in_progress"
                )

                # Assert
                assert result.status == OrderStatus.in_progress
                mock_event_publisher["order_status_changed"].assert_called_once()

    @pytest.mark.asyncio
    async def test_update_order_status_to_completed(self, mock_db, mock_event_publisher):
        """Test updating order status to completed."""
        # Arrange
        in_progress_order = Order(
            id=3,
            customer_id=10,
            provider_id=20,
            title="Test Order",
            description="Test description",
            service_type=ServiceType.CLEANING_REPAIR,
            status=OrderStatus.in_progress,
            price=100.00,
            location=LocationEnum.NORTH,
            address="123 Test St",
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        completed_order = Order(
            id=in_progress_order.id,
            customer_id=in_progress_order.customer_id,
            provider_id=in_progress_order.provider_id,
            title=in_progress_order.title,
            description=in_progress_order.description,
            service_type=in_progress_order.service_type,
            status=OrderStatus.completed,
            price=in_progress_order.price,
            location=in_progress_order.location,
            address=in_progress_order.address,
            payment_status=in_progress_order.payment_status,
            created_at=in_progress_order.created_at,
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=in_progress_order):
            with patch.object(OrderDAO, "update_order_status", new_callable=AsyncMock, return_value=completed_order):
                # Act
                result = await ProviderOrderService.update_order_status(
                    db=mock_db, provider_id=20, order_id=3, new_status="completed"
                )

                # Assert
                assert result.status == OrderStatus.completed
                mock_event_publisher["order_status_changed"].assert_called_once()

    @pytest.mark.asyncio
    async def test_update_order_status_permission_denied(self, mock_db, sample_accepted_order):
        """Test updating order status with wrong provider_id."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_accepted_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.update_order_status(
                    db=mock_db, provider_id=999, order_id=1, new_status="in_progress"
                )

            assert exc_info.value.status_code == 403
            assert "permission denied" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_order_status_invalid_transition(self, mock_db):
        """Test invalid status transition (pending -> in_progress)."""
        # Arrange - pending order with provider_id set
        pending_order_with_provider = Order(
            id=1,
            customer_id=10,
            provider_id=20,
            title="Test Order",
            description="Test description",
            service_type=ServiceType.CLEANING_REPAIR,
            status=OrderStatus.pending,
            price=100.00,
            location=LocationEnum.NORTH,
            address="123 Test St",
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=pending_order_with_provider):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.update_order_status(
                    db=mock_db, provider_id=20, order_id=1, new_status="in_progress"
                )

            assert exc_info.value.status_code == 400
            assert "must be accepted before starting" in exc_info.value.detail.lower()


class TestProviderOrderServiceGetOrderHistory:
    """Test getting order history."""

    @pytest.mark.asyncio
    async def test_get_order_history_success(self, mock_db):
        """Test successfully getting provider order history."""
        # Arrange
        provider_orders = [
            Order(
                id=1,
                customer_id=10,
                provider_id=20,
                title="Order 1",
                description="Description 1",
                service_type=ServiceType.CLEANING_REPAIR,
                status=OrderStatus.completed,
                price=100.00,
                location=LocationEnum.NORTH,
                address="123 Test St",
                payment_status=PaymentStatus.paid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Order(
                id=2,
                customer_id=11,
                provider_id=20,
                title="Order 2",
                description="Description 2",
                service_type=ServiceType.LIFE_HEALTH,
                status=OrderStatus.in_progress,
                price=150.00,
                location=LocationEnum.SOUTH,
                address="456 Test Ave",
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

        with patch.object(OrderDAO, "get_provider_orders", new_callable=AsyncMock, return_value=provider_orders):
            # Act
            result = await ProviderOrderService.get_order_history(db=mock_db, provider_id=20)

            # Assert
            assert len(result) == 2
            assert all(order.provider_id == 20 for order in result)


class TestProviderOrderServiceGetOrderDetail:
    """Test getting order details."""

    @pytest.mark.asyncio
    async def test_get_order_detail_success(self, mock_db, sample_accepted_order):
        """Test successfully getting order detail."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_accepted_order):
            # Act
            result = await ProviderOrderService.get_order_detail(db=mock_db, provider_id=20, order_id=1)

            # Assert
            assert result.id == sample_accepted_order.id
            assert result.provider_id == 20

    @pytest.mark.asyncio
    async def test_get_order_detail_not_found(self, mock_db):
        """Test getting non-existent order detail."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.get_order_detail(db=mock_db, provider_id=20, order_id=999)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_order_detail_permission_denied(self, mock_db, sample_accepted_order):
        """Test getting order detail with wrong provider_id."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_accepted_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await ProviderOrderService.get_order_detail(db=mock_db, provider_id=999, order_id=1)

            assert exc_info.value.status_code == 403
            assert "permission denied" in exc_info.value.detail.lower()
