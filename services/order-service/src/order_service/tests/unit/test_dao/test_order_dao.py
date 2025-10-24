"""Tests for OrderDAO."""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest

from order_service.dao.order_dao import OrderDAO
from order_service.models.order import Order, OrderStatus, PaymentStatus, ServiceType, LocationEnum


class TestOrderDAOCreate:
    """Test OrderDAO.create_order method."""

    @pytest.mark.asyncio
    async def test_create_order_success(self, mock_db):
        """Test successfully creating an order."""
        # Arrange
        created_order = Order(
            id=1,
            customer_id=10,
            title="Test Order",
            description="Test description",
            service_type=ServiceType.CLEANING_REPAIR,
            status=OrderStatus.pending_review,
            price=100.00,
            location=LocationEnum.NORTH,
            address="123 Test St",
            service_start_time=datetime(2024, 1, 20, 10, 0),
            service_end_time=datetime(2024, 1, 20, 14, 0),
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", 1))

        # Act
        order = await OrderDAO.create_order(
            db=mock_db,
            customer_id=10,
            title="Test Order",
            description="Test description",
            service_type=ServiceType.CLEANING_REPAIR,
            price=100.00,
            location=LocationEnum.NORTH,
            address="123 Test St",
            service_start_time=datetime(2024, 1, 20, 10, 0),
            service_end_time=datetime(2024, 1, 20, 14, 0),
        )

        # Assert
        assert order.customer_id == 10
        assert order.title == "Test Order"
        assert order.status == OrderStatus.pending_review
        assert order.payment_status == PaymentStatus.unpaid
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestOrderDAOGet:
    """Test OrderDAO get methods."""

    @pytest.mark.asyncio
    async def test_get_order_by_id_success(self, mock_db, sample_order):
        """Test getting order by ID successfully."""
        mock_db.get = AsyncMock(return_value=sample_order)

        order = await OrderDAO.get_order_by_id(mock_db, 1)

        assert order is not None
        assert order.id == 1
        assert order.title == "Home Cleaning Service"
        mock_db.get.assert_called_once_with(Order, 1)

    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self, mock_db):
        """Test getting order when it doesn't exist."""
        mock_db.get = AsyncMock(return_value=None)

        order = await OrderDAO.get_order_by_id(mock_db, 999)

        assert order is None
        mock_db.get.assert_called_once_with(Order, 999)

    @pytest.mark.asyncio
    async def test_get_customer_orders_success(self, mock_db, sample_order, sample_pending_order):
        """Test getting customer orders list."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[sample_order, sample_pending_order])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await OrderDAO.get_customer_orders(mock_db, 10)

        assert len(orders) == 2
        assert orders[0].customer_id == 10
        assert orders[1].customer_id == 10
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_customer_orders_with_status_filter(self, mock_db, sample_pending_order):
        """Test getting customer orders filtered by status."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[sample_pending_order])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await OrderDAO.get_customer_orders(mock_db, 10, statuses=[OrderStatus.pending])

        assert len(orders) == 1
        assert orders[0].status == OrderStatus.pending
        mock_db.execute.assert_called_once()


class TestOrderDAOUpdate:
    """Test OrderDAO update methods."""

    @pytest.mark.asyncio
    async def test_update_order_status_success(self, mock_db, sample_order):
        """Test updating order status successfully."""
        mock_db.get = AsyncMock(return_value=sample_order)

        updated_order = await OrderDAO.update_order_status(mock_db, 1, OrderStatus.pending)

        assert updated_order is not None
        assert updated_order.status == OrderStatus.pending
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_order_status_not_found(self, mock_db):
        """Test updating status when order doesn't exist."""
        mock_db.get = AsyncMock(return_value=None)

        updated_order = await OrderDAO.update_order_status(mock_db, 999, OrderStatus.pending)

        assert updated_order is None
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_accept_order_success(self, mock_db, sample_pending_order):
        """Test accepting an order."""
        mock_db.get = AsyncMock(return_value=sample_pending_order)

        updated_order = await OrderDAO.accept_order(mock_db, 2, provider_id=20)

        assert updated_order is not None
        assert updated_order.provider_id == 20
        assert updated_order.status == OrderStatus.accepted
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_payment_status_success(self, mock_db, sample_order):
        """Test updating payment status."""
        mock_db.get = AsyncMock(return_value=sample_order)

        updated_order = await OrderDAO.update_payment_status(mock_db, 1, PaymentStatus.paid)

        assert updated_order is not None
        assert updated_order.payment_status == PaymentStatus.paid
        mock_db.commit.assert_called_once()


class TestOrderDAODelete:
    """Test OrderDAO delete method."""

    @pytest.mark.asyncio
    async def test_delete_order_success(self, mock_db, sample_order):
        """Test deleting an order successfully."""
        mock_db.get = AsyncMock(return_value=sample_order)

        result = await OrderDAO.delete_order(mock_db, 1)

        assert result is True
        mock_db.delete.assert_called_once_with(sample_order)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_order_not_found(self, mock_db):
        """Test deleting non-existent order."""
        mock_db.get = AsyncMock(return_value=None)

        result = await OrderDAO.delete_order(mock_db, 999)

        assert result is False
        mock_db.delete.assert_not_called()
