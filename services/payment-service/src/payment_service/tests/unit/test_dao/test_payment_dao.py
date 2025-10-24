"""
Unit tests for PaymentDAO.

Tests cover:
- Creating payments
- Getting payments by ID
- Getting payments by order ID
- Updating payment status
- Getting user payments
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from payment_service.dao.payment_dao import PaymentDAO
from payment_service.models.payment import Payment, PaymentMethod, PaymentStatus


class TestPaymentDAOCreate:
    """Test payment creation operations."""

    @pytest.mark.asyncio
    async def test_create_payment_success(self, mock_db):
        """Test successfully creating a payment."""
        # Arrange
        created_payment = Payment(
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

        async def mock_refresh(payment):
            payment.id = 1
            payment.transaction_id = "test-txn-001"

        mock_db.refresh.side_effect = mock_refresh

        # Act
        result = await PaymentDAO.create_payment(
            db=mock_db, order_id=100, customer_id=10, provider_id=20, amount=150.00
        )

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.order_id == 100
        assert result.customer_id == 10
        assert result.amount == 150.00
        assert result.status == PaymentStatus.pending


class TestPaymentDAOGet:
    """Test payment retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_payment_by_id_success(self, mock_db, sample_payment):
        """Test successfully getting payment by ID."""
        # Arrange
        mock_db.get.return_value = sample_payment

        # Act
        result = await PaymentDAO.get_payment_by_id(mock_db, payment_id=1)

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.order_id == 100
        mock_db.get.assert_called_once_with(Payment, 1)

    @pytest.mark.asyncio
    async def test_get_payment_by_id_not_found(self, mock_db):
        """Test getting non-existent payment by ID."""
        # Arrange
        mock_db.get.return_value = None

        # Act
        result = await PaymentDAO.get_payment_by_id(mock_db, payment_id=999)

        # Assert
        assert result is None
        mock_db.get.assert_called_once_with(Payment, 999)

    @pytest.mark.asyncio
    async def test_get_payment_by_order_id_success(self, mock_db, sample_payment):
        """Test successfully getting payment by order ID."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_payment
        mock_db.execute.return_value = mock_result

        # Act
        result = await PaymentDAO.get_payment_by_order_id(mock_db, order_id=100)

        # Assert
        assert result is not None
        assert result.order_id == 100
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_payment_by_order_id_not_found(self, mock_db):
        """Test getting payment for non-existent order."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        # Act
        result = await PaymentDAO.get_payment_by_order_id(mock_db, order_id=999)

        # Assert
        assert result is None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_payments_success(self, mock_db):
        """Test successfully getting user's payment history."""
        # Arrange
        user_payments = [
            Payment(
                id=1,
                order_id=100,
                customer_id=10,
                provider_id=20,
                amount=150.00,
                payment_method=PaymentMethod.simulated,
                status=PaymentStatus.completed,
                transaction_id="test-txn-001",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Payment(
                id=2,
                order_id=101,
                customer_id=10,
                provider_id=21,
                amount=200.00,
                payment_method=PaymentMethod.simulated,
                status=PaymentStatus.completed,
                transaction_id="test-txn-002",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = user_payments
        mock_db.execute.return_value = mock_result

        # Act
        result = await PaymentDAO.get_user_payments(mock_db, user_id=10)

        # Assert
        assert len(result) == 2
        assert all(payment.customer_id == 10 for payment in result)
        mock_db.execute.assert_called_once()


class TestPaymentDAOUpdate:
    """Test payment update operations."""

    @pytest.mark.asyncio
    async def test_update_payment_status_success(self, mock_db, sample_payment):
        """Test successfully updating payment status."""
        # Arrange
        mock_db.get.return_value = sample_payment

        # Act
        result = await PaymentDAO.update_payment_status(mock_db, payment_id=1, status=PaymentStatus.completed)

        # Assert
        assert result is not None
        assert result.status == PaymentStatus.completed
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_payment_status_not_found(self, mock_db):
        """Test updating status of non-existent payment."""
        # Arrange
        mock_db.get.return_value = None

        # Act
        result = await PaymentDAO.update_payment_status(mock_db, payment_id=999, status=PaymentStatus.completed)

        # Assert
        assert result is None
        mock_db.commit.assert_not_called()
