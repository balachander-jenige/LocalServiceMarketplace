"""
Unit tests for AdminOrderService.

Tests cover admin order operations including:
- Getting all orders (with status filter)
- Approving/rejecting orders
- Updating order information
- Deleting orders
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from order_service.dao.order_dao import OrderDAO
from order_service.models.order import LocationEnum, Order, OrderStatus, PaymentStatus, ServiceType
from order_service.services.admin_order_service import AdminOrderService


class TestAdminOrderServiceGetAllOrders:
    """Test getting all orders."""

    @pytest.mark.asyncio
    async def test_get_all_orders_without_filter(self, mock_db):
        """Test getting all orders without status filter."""
        # Arrange
        all_orders = [
            Order(
                id=1,
                customer_id=10,
                title="Order 1",
                description="Description 1",
                service_type=ServiceType.CLEANING_REPAIR,
                status=OrderStatus.pending_review,
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
                title="Order 2",
                description="Description 2",
                service_type=ServiceType.IT_TECHNOLOGY,
                status=OrderStatus.pending,
                price=150.00,
                location=LocationEnum.SOUTH,
                address="456 Test Ave",
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

        with patch.object(OrderDAO, "get_all_orders", new_callable=AsyncMock, return_value=all_orders):
            # Act
            result = await AdminOrderService.get_all_orders(db=mock_db)

            # Assert
            assert len(result) == 2
            assert result[0].id == 1
            assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_get_all_orders_with_status_filter(self, mock_db):
        """Test getting orders filtered by status."""
        # Arrange
        pending_orders = [
            Order(
                id=2,
                customer_id=11,
                title="Order 2",
                description="Description 2",
                service_type=ServiceType.EDUCATION_TRAINING,
                status=OrderStatus.pending,
                price=150.00,
                location=LocationEnum.SOUTH,
                address="456 Test Ave",
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

        with patch.object(OrderDAO, "get_orders_by_status", new_callable=AsyncMock, return_value=pending_orders):
            # Act
            result = await AdminOrderService.get_all_orders(db=mock_db, status_filter="pending")

            # Assert
            assert len(result) == 1
            assert result[0].status == OrderStatus.pending

    @pytest.mark.asyncio
    async def test_get_all_orders_invalid_status_filter(self, mock_db):
        """Test getting orders with invalid status filter."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await AdminOrderService.get_all_orders(db=mock_db, status_filter="invalid_status")

        assert exc_info.value.status_code == 400
        assert "invalid status" in exc_info.value.detail.lower()


class TestAdminOrderServiceGetPendingReviewOrders:
    """Test getting pending review orders."""

    @pytest.mark.asyncio
    async def test_get_pending_review_orders_success(self, mock_db):
        """Test successfully getting pending review orders."""
        # Arrange
        pending_review_orders = [
            Order(
                id=1,
                customer_id=10,
                title="Order 1",
                description="Description 1",
                service_type=ServiceType.CLEANING_REPAIR,
                status=OrderStatus.pending_review,
                price=100.00,
                location=LocationEnum.NORTH,
                address="123 Test St",
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

        with patch.object(
            OrderDAO, "get_orders_by_status", new_callable=AsyncMock, return_value=pending_review_orders
        ):
            # Act
            result = await AdminOrderService.get_pending_review_orders(db=mock_db)

            # Assert
            assert len(result) == 1
            assert result[0].status == OrderStatus.pending_review


class TestAdminOrderServiceApproveOrder:
    """Test approving and rejecting orders."""

    @pytest.mark.asyncio
    async def test_approve_order_success(self, mock_db, sample_order, mock_event_publisher):
        """Test successfully approving an order."""
        # Arrange
        approved_order = Order(
            id=sample_order.id,
            customer_id=sample_order.customer_id,
            title=sample_order.title,
            description=sample_order.description,
            service_type=sample_order.service_type,
            status=OrderStatus.pending,
            price=sample_order.price,
            location=sample_order.location,
            address=sample_order.address,
            payment_status=sample_order.payment_status,
            created_at=sample_order.created_at,
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            with patch.object(OrderDAO, "update_order_status", new_callable=AsyncMock, return_value=approved_order):
                # Act
                result = await AdminOrderService.approve_order(db=mock_db, order_id=1, approved=True)

                # Assert
                assert result.status == OrderStatus.pending
                mock_event_publisher["order_approved"].assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_order_success(self, mock_db, sample_order, mock_event_publisher):
        """Test successfully rejecting an order."""
        # Arrange
        rejected_order = Order(
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
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            with patch.object(OrderDAO, "update_order_status", new_callable=AsyncMock, return_value=rejected_order):
                # Act
                result = await AdminOrderService.approve_order(
                    db=mock_db, order_id=1, approved=False, reject_reason="Quality issues"
                )

                # Assert
                assert result.status == OrderStatus.cancelled
                mock_event_publisher["order_rejected"].assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_order_not_found(self, mock_db):
        """Test approving non-existent order."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.approve_order(db=mock_db, order_id=999, approved=True)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_approve_order_invalid_status(self, mock_db, sample_pending_order):
        """Test approving order with wrong status (not pending_review)."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_pending_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.approve_order(db=mock_db, order_id=1, approved=True)

            assert exc_info.value.status_code == 400
            assert "pending_review" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_reject_order_without_reason(self, mock_db, sample_order):
        """Test rejecting order without providing reason."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.approve_order(db=mock_db, order_id=1, approved=False, reject_reason=None)

            assert exc_info.value.status_code == 400
            assert "reason is required" in exc_info.value.detail.lower()


class TestAdminOrderServiceUpdateOrder:
    """Test updating order information."""

    @pytest.mark.asyncio
    async def test_update_order_success(self, mock_db, sample_order):
        """Test successfully updating order information."""
        # Arrange
        updated_order = Order(
            id=sample_order.id,
            customer_id=sample_order.customer_id,
            title="Updated Title",
            description="Updated Description",
            service_type=sample_order.service_type,
            status=sample_order.status,
            price=150.00,
            location=sample_order.location,
            address=sample_order.address,
            payment_status=sample_order.payment_status,
            created_at=sample_order.created_at,
            updated_at=datetime.now(UTC),
        )

        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            with patch.object(OrderDAO, "update_order", new_callable=AsyncMock, return_value=updated_order):
                # Act
                result = await AdminOrderService.update_order(
                    db=mock_db, order_id=1, title="Updated Title", description="Updated Description", price=150.00
                )

                # Assert
                assert result.title == "Updated Title"
                assert result.price == 150.00

    @pytest.mark.asyncio
    async def test_update_order_not_found(self, mock_db):
        """Test updating non-existent order."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.update_order(db=mock_db, order_id=999, title="Updated")

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_order_invalid_service_type(self, mock_db, sample_order):
        """Test updating order with invalid service type."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.update_order(db=mock_db, order_id=1, service_type="invalid_type")

            assert exc_info.value.status_code == 400
            assert "invalid service_type" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_order_invalid_price(self, mock_db, sample_order):
        """Test updating order with invalid price (negative or zero)."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.update_order(db=mock_db, order_id=1, price=-10.0)

            assert exc_info.value.status_code == 400
            assert "price must be positive" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_order_no_fields(self, mock_db, sample_order):
        """Test updating order without providing any fields."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.update_order(db=mock_db, order_id=1)

            assert exc_info.value.status_code == 400
            assert "no valid fields to update" in exc_info.value.detail.lower()


class TestAdminOrderServiceDeleteOrder:
    """Test deleting orders."""

    @pytest.mark.asyncio
    async def test_delete_order_success(self, mock_db, sample_order):
        """Test successfully deleting an order."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            with patch.object(OrderDAO, "delete_order", new_callable=AsyncMock, return_value=True):
                # Act
                result = await AdminOrderService.delete_order(db=mock_db, order_id=1)

                # Assert
                assert result is True

    @pytest.mark.asyncio
    async def test_delete_order_not_found(self, mock_db):
        """Test deleting non-existent order."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.delete_order(db=mock_db, order_id=999)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()


class TestAdminOrderServiceGetOrderDetail:
    """Test getting order details."""

    @pytest.mark.asyncio
    async def test_get_order_detail_success(self, mock_db, sample_order):
        """Test successfully getting order detail."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=sample_order):
            # Act
            result = await AdminOrderService.get_order_detail(db=mock_db, order_id=1)

            # Assert
            assert result.id == sample_order.id
            assert result.customer_id == sample_order.customer_id

    @pytest.mark.asyncio
    async def test_get_order_detail_not_found(self, mock_db):
        """Test getting non-existent order detail."""
        with patch.object(OrderDAO, "get_order_by_id", new_callable=AsyncMock, return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await AdminOrderService.get_order_detail(db=mock_db, order_id=999)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()
