"""
Unit tests for RefundService.

Tests cover:
- Successful refund processing
- Payment not found scenarios
- Permission validation
- Duplicate refund prevention
- Event publishing verification
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from payment_service.models.payment import Payment, PaymentMethod, PaymentStatus
from payment_service.models.refund import Refund, RefundStatus
from payment_service.services.refund_service import RefundService


class TestRefundServiceProcessRefund:
    """Test refund processing operations."""

    @pytest.mark.asyncio
    async def test_process_refund_success(self, mock_db, sample_completed_payment):
        """Test successfully processing a refund."""
        # Arrange
        user_id = 10
        order_id = 100
        reason = "Customer requested refund"

        with patch("payment_service.services.refund_service.PaymentDAO") as mock_payment_dao, \
             patch("payment_service.services.refund_service.RefundDAO") as mock_refund_dao, \
             patch("payment_service.services.refund_service.TransactionDAO") as mock_transaction_dao, \
             patch("payment_service.services.refund_service.EventPublisher") as mock_event_publisher:
            
            # Mock payment retrieval
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=sample_completed_payment)
            
            # Mock no existing refund
            mock_refund_dao.get_refund_by_order_id = AsyncMock(return_value=None)
            
            # Mock refund creation
            created_refund = Refund(
                id=1,
                payment_id=sample_completed_payment.id,
                order_id=order_id,
                customer_id=user_id,
                amount=150.00,
                reason=reason,
                status=RefundStatus.pending,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            mock_refund_dao.create_refund = AsyncMock(return_value=created_refund)
            
            # Mock transaction creation
            mock_transaction_dao.create_transaction = AsyncMock()
            
            # Mock status update
            mock_refund_dao.update_refund_status = AsyncMock()
            
            # Mock event publishing
            mock_event_publisher.publish_refund_processed = AsyncMock()

            # Act
            result = await RefundService.process_refund(
                db=mock_db, user_id=user_id, order_id=order_id, reason=reason
            )

            # Assert
            assert result["refund_id"] == 1
            assert result["order_id"] == order_id
            assert result["amount"] == float(sample_completed_payment.amount)
            assert result["status"] == RefundStatus.completed.value
            assert "退款成功" in result["message"]
            
            # Verify payment retrieval
            mock_payment_dao.get_payment_by_order_id.assert_called_once_with(mock_db, order_id)
            
            # Verify refund creation
            mock_refund_dao.create_refund.assert_called_once_with(
                db=mock_db,
                payment_id=sample_completed_payment.id,
                order_id=order_id,
                customer_id=user_id,
                amount=float(sample_completed_payment.amount),
                reason=reason,
            )
            
            # Verify transaction creation
            mock_transaction_dao.create_transaction.assert_called_once()
            
            # Verify status update
            mock_refund_dao.update_refund_status.assert_called_once_with(
                mock_db, 1, RefundStatus.completed
            )
            
            # Verify event publishing
            mock_event_publisher.publish_refund_processed.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_refund_payment_not_found(self, mock_db):
        """Test refund when payment doesn't exist."""
        # Arrange
        with patch("payment_service.services.refund_service.PaymentDAO") as mock_payment_dao:
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await RefundService.process_refund(db=mock_db, user_id=10, order_id=999)
            
            assert exc_info.value.status_code == 404
            assert "Payment not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_refund_permission_denied(self, mock_db):
        """Test refund when user is not the payment customer."""
        # Arrange
        other_user_payment = Payment(
            id=1,
            order_id=100,
            customer_id=999,  # Different user
            provider_id=20,
            amount=150.00,
            payment_method=PaymentMethod.simulated,
            status=PaymentStatus.completed,
            transaction_id="test-txn-001",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with patch("payment_service.services.refund_service.PaymentDAO") as mock_payment_dao:
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=other_user_payment)

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await RefundService.process_refund(db=mock_db, user_id=10, order_id=100)
            
            assert exc_info.value.status_code == 403
            assert "Permission denied" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_refund_already_processed(self, mock_db, sample_completed_payment):
        """Test refund when refund already exists."""
        # Arrange
        existing_refund = Refund(
            id=1,
            payment_id=sample_completed_payment.id,
            order_id=100,
            customer_id=10,
            amount=150.00,
            reason="Previous refund",
            status=RefundStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        with patch("payment_service.services.refund_service.PaymentDAO") as mock_payment_dao, \
             patch("payment_service.services.refund_service.RefundDAO") as mock_refund_dao:
            
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=sample_completed_payment)
            mock_refund_dao.get_refund_by_order_id = AsyncMock(return_value=existing_refund)

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await RefundService.process_refund(db=mock_db, user_id=10, order_id=100)
            
            assert exc_info.value.status_code == 400
            assert "Refund already processed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_refund_without_reason(self, mock_db, sample_completed_payment):
        """Test refund without providing a reason."""
        # Arrange
        user_id = 10
        order_id = 100

        with patch("payment_service.services.refund_service.PaymentDAO") as mock_payment_dao, \
             patch("payment_service.services.refund_service.RefundDAO") as mock_refund_dao, \
             patch("payment_service.services.refund_service.TransactionDAO") as mock_transaction_dao, \
             patch("payment_service.services.refund_service.EventPublisher") as mock_event_publisher:
            
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=sample_completed_payment)
            mock_refund_dao.get_refund_by_order_id = AsyncMock(return_value=None)
            
            created_refund = Refund(
                id=1,
                payment_id=sample_completed_payment.id,
                order_id=order_id,
                customer_id=user_id,
                amount=150.00,
                reason=None,  # No reason provided
                status=RefundStatus.pending,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            mock_refund_dao.create_refund = AsyncMock(return_value=created_refund)
            mock_transaction_dao.create_transaction = AsyncMock()
            mock_refund_dao.update_refund_status = AsyncMock()
            mock_event_publisher.publish_refund_processed = AsyncMock()

            # Act
            result = await RefundService.process_refund(
                db=mock_db, user_id=user_id, order_id=order_id, reason=None
            )

            # Assert
            assert result["refund_id"] == 1
            assert result["order_id"] == order_id
            
            # Verify refund created with None reason
            mock_refund_dao.create_refund.assert_called_once()
            call_kwargs = mock_refund_dao.create_refund.call_args.kwargs
            assert call_kwargs["reason"] is None
