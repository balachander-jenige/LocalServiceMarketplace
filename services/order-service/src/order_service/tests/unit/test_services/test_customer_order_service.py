"""Tests for CustomerOrderService."""

from datetime import datetime, UTC
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from order_service.dao.order_dao import OrderDAO
from order_service.models.order import Order, OrderStatus, PaymentStatus, ServiceType, LocationEnum
from order_service.services.customer_order_service import CustomerOrderService


class TestCustomerOrderServicePublishOrder:
    """Test CustomerOrderService.publish_order method."""

    @pytest.mark.asyncio
    async def test_publish_order_success(self, mock_db, mock_event_publisher):
        """Test successfully publishing an order."""
        # Arrange
        created_order = Order(
            id=1,
            customer_id=10,
            title="Test Service",
            description="Test description",
            service_type=ServiceType.CLEANING_REPAIR,
            status=OrderStatus.pending_review,
            price=100.00,
            location=LocationEnum.NORTH,
            address="123 Test St",
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "create_order", new_callable=AsyncMock, return_value=created_order):
            # Act
            order = await CustomerOrderService.publish_order(
                db=mock_db,
                customer_id=10,
                title="Test Service",
                description="Test description",
                service_type="cleaning_repair",
                price=100.00,
                location="NORTH",
                address="123 Test St",
            )

            # Assert
            assert order.customer_id == 10
            assert order.title == "Test Service"
            assert order.status == OrderStatus.pending_review
            mock_event_publisher["order_created"].assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_order_with_service_time(self, mock_db, mock_event_publisher):
        """Test publishing order with service time."""
        created_order = Order(
            id=2,
            customer_id=10,
            title="Scheduled Service",
            description="Need service at specific time",
            service_type=ServiceType.IT_TECHNOLOGY,
            status=OrderStatus.pending_review,
            price=200.00,
            location=LocationEnum.MID,
            address="456 Tech St",
            service_start_time=datetime(2024, 1, 25, 10, 0),
            service_end_time=datetime(2024, 1, 25, 14, 0),
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "create_order", new_callable=AsyncMock, return_value=created_order):
            order = await CustomerOrderService.publish_order(
                db=mock_db,
                customer_id=10,
                title="Scheduled Service",
                description="Need service at specific time",
                service_type="it_technology",
                price=200.00,
                location="MID",
                address="456 Tech St",
                service_start_time=datetime(2024, 1, 25, 10, 0),
                service_end_time=datetime(2024, 1, 25, 14, 0),
            )

            assert order.service_start_time is not None
            assert order.service_end_time is not None


class TestCustomerOrderServiceCancelOrder:
    """Test CustomerOrderService.cancel_order method."""

    @pytest.mark.asyncio
    async def test_cancel_order_success(self, mock_db, sample_order, mock_event_publisher):
        """Test successfully cancelling an order."""
        # Create cancelled order
        cancelled_order = Order(
            id=sample_order.id,
            customer_id=sample_order.customer_id,
            title=sample_order.title,
            description=sample_order.description,
            service_type=sample_order.service_type,
            status=OrderStatus.cancelled,
            price=sample_order.price,
            location=sample_order.location,
            address=sample_order.address,
            payment_status=sample_order.payment_status,
            created_at=sample_order.created_at,
            updated_at=sample_order.updated_at,
        )
        
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            with patch.object(
                OrderDAO,
                "update_order_status",
                new_callable=AsyncMock,
                return_value=cancelled_order,
            ):
                order = await CustomerOrderService.cancel_order(mock_db, customer_id=10, order_id=1)

                assert order.status == OrderStatus.cancelled
                mock_event_publisher["order_cancelled"].assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_order_not_found(self, mock_db):
        """Test cancelling non-existent order."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.cancel_order(mock_db, customer_id=10, order_id=999)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_cancel_order_permission_denied(self, mock_db, sample_order):
        """Test cancelling order with wrong customer_id."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.cancel_order(mock_db, customer_id=999, order_id=1)

            assert exc_info.value.status_code == 403
            assert "permission denied" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_cancel_order_invalid_status(self, mock_db):
        """Test cancelling order in invalid status."""
        completed_order = Order(
            id=1,
            customer_id=10,
            provider_id=20,
            title="Completed Order",
            description="Already completed",
            service_type=ServiceType.CLEANING_REPAIR,
            status=OrderStatus.completed,
            price=100.00,
            location=LocationEnum.NORTH,
            address="123 Test St",
            payment_status=PaymentStatus.paid,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=completed_order):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.cancel_order(mock_db, customer_id=10, order_id=1)

            assert exc_info.value.status_code == 400
            assert "cannot be cancelled" in exc_info.value.detail.lower()


class TestCustomerOrderServiceGetOrders:
    """Test CustomerOrderService get methods."""

    @pytest.mark.asyncio
    async def test_get_my_orders_success(self, mock_db, sample_order, sample_pending_order):
        """Test getting my orders."""
        with patch.object(
            OrderDAO, "get_customer_orders", new_callable=AsyncMock, return_value=[sample_order, sample_pending_order]
        ):
            orders = await CustomerOrderService.get_my_orders(mock_db, customer_id=10)

            assert len(orders) == 2
            assert all(order.customer_id == 10 for order in orders)

    @pytest.mark.asyncio
    async def test_get_order_detail_success(self, mock_db, sample_order):
        """Test getting order detail."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            order = await CustomerOrderService.get_order_detail(mock_db, customer_id=10, order_id=1)

            assert order.id == 1
            assert order.customer_id == 10

    @pytest.mark.asyncio
    async def test_get_order_detail_not_found(self, mock_db):
        """Test getting non-existent order detail."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.get_order_detail(mock_db, customer_id=10, order_id=999)

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_order_detail_permission_denied(self, mock_db, sample_order):
        """Test getting order detail with wrong customer_id."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.get_order_detail(mock_db, customer_id=999, order_id=1)

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_order_history_success(self, mock_db, sample_order):
        """Test getting order history."""
        with patch.object(OrderDAO, "get_customer_orders", new_callable=AsyncMock, return_value=[sample_order]):
            orders = await CustomerOrderService.get_order_history(mock_db, customer_id=10)

            assert len(orders) == 1
            assert orders[0].customer_id == 10
