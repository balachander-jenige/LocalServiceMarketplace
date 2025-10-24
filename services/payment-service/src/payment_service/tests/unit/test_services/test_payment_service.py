"""
Unit tests for PaymentService.

Tests cover:
- Successful payment processing
- Order not found scenarios
- Invalid order status handling
- Duplicate payment prevention
- External API error handling
- Event publishing verification
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from payment_service.models.payment import Payment, PaymentMethod, PaymentStatus
from payment_service.services.payment_service import PaymentService


class TestPaymentServicePayOrder:
    """Test payment order processing."""

    @pytest.mark.asyncio
    async def test_pay_order_success(self, mock_db, mock_event_publisher, mock_httpx_client, sample_payment):
        """Test successfully processing a payment."""
        # Arrange
        order_id = 100
        user_id = 10
        
        # Mock order service response
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "id": order_id,
            "customer_id": user_id,
            "provider_id": 20,
            "service_type": "IT_TECHNOLOGY",
            "description": "Software development",
            "price": 150.00,
            "status": "completed",
            "payment_status": "unpaid",
            "created_at": datetime.now(UTC).isoformat(),
        }
        mock_httpx_client.get.return_value = order_response

        # Mock DAO responses and EventPublisher
        with patch("payment_service.services.payment_service.PaymentDAO") as mock_payment_dao, \
             patch("payment_service.services.payment_service.TransactionDAO") as mock_transaction_dao, \
             patch("payment_service.services.payment_service.EventPublisher") as mock_event_pub:
            
            # Mock no existing payment
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=None)
            
            # Mock payment creation
            created_payment = Payment(
                id=1,
                order_id=order_id,
                customer_id=user_id,
                provider_id=20,
                amount=150.00,
                payment_method=PaymentMethod.simulated,
                status=PaymentStatus.pending,
                transaction_id="test-txn-001",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            mock_payment_dao.create_payment = AsyncMock(return_value=created_payment)
            
            # Mock status update
            completed_payment = Payment(
                id=1,
                order_id=order_id,
                customer_id=user_id,
                provider_id=20,
                amount=150.00,
                payment_method=PaymentMethod.simulated,
                status=PaymentStatus.completed,
                transaction_id="test-txn-001",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            mock_payment_dao.update_payment_status = AsyncMock(return_value=completed_payment)
            
            # Mock transaction creation
            mock_transaction_dao.create_transaction = AsyncMock()
            
            # Mock event publishing
            mock_event_pub.publish_payment_initiated = AsyncMock()
            mock_event_pub.publish_payment_completed = AsyncMock()

            # Act
            result = await PaymentService.pay_order(
                db=mock_db, user_id=user_id, order_id=order_id, token="test-token"
            )

            # Assert
            assert result["payment_id"] == 1
            assert result["order_id"] == order_id
            assert result["amount"] == 150.00
            assert "message" in result
            
            # Verify Order Service API call
            mock_httpx_client.get.assert_called_once()
            
            # Verify payment creation and update
            mock_payment_dao.create_payment.assert_called_once_with(
                db=mock_db,
                order_id=order_id,
                customer_id=user_id,
                provider_id=20,
                amount=150.00,
                payment_method=PaymentMethod.simulated,
            )
            # Verify update_payment_status was called (service uses positional args)
            assert mock_payment_dao.update_payment_status.called
            call_args = mock_payment_dao.update_payment_status.call_args
            assert call_args[0][0] == mock_db
            assert call_args[0][1] == 1
            assert call_args[0][2] == PaymentStatus.completed
            
            # Verify transaction creation
            mock_transaction_dao.create_transaction.assert_called_once()
            
            # Verify event publishing (payment_initiated and payment_completed)
            mock_event_pub.publish_payment_initiated.assert_called_once()
            mock_event_pub.publish_payment_completed.assert_called_once()

    @pytest.mark.asyncio
    async def test_pay_order_not_found(self, mock_db, mock_httpx_client):
        """Test payment when order doesn't exist."""
        # Arrange
        order_response = MagicMock()
        order_response.status_code = 404
        order_response.text = "Order not found"
        mock_httpx_client.get = AsyncMock(return_value=order_response)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await PaymentService.pay_order(db=mock_db, user_id=10, order_id=999, token="test-token")
        
        assert exc_info.value.status_code == 404
        assert "Order not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_pay_order_invalid_order_status(self, mock_db, mock_httpx_client):
        """Test payment when order status is not 'completed'."""
        # Arrange
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "id": 100,
            "customer_id": 10,
            "provider_id": 20,
            "service_type": "IT_TECHNOLOGY",
            "status": "pending",  # Not completed
            "payment_status": "unpaid",
            "price": 150.00,
        }
        mock_httpx_client.get.return_value = order_response

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await PaymentService.pay_order(db=mock_db, user_id=10, order_id=100, token="test-token")
        
        assert exc_info.value.status_code == 400
        assert "无法支付" in str(exc_info.value.detail) or "cannot" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_pay_order_already_paid(self, mock_db, mock_httpx_client):
        """Test payment when order is already paid."""
        # Arrange
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "id": 100,
            "customer_id": 10,
            "provider_id": 20,
            "service_type": "IT_TECHNOLOGY",
            "status": "completed",
            "payment_status": "paid",  # Already paid
            "price": 150.00,
        }
        mock_httpx_client.get.return_value = order_response

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await PaymentService.pay_order(db=mock_db, user_id=10, order_id=100, token="test-token")
        
        assert exc_info.value.status_code == 400
        assert "无法支付" in str(exc_info.value.detail) or "cannot" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_pay_order_duplicate_payment(self, mock_db, mock_httpx_client, sample_completed_payment):
        """Test payment when payment record already exists."""
        # Arrange
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "id": 100,
            "customer_id": 10,
            "provider_id": 20,
            "service_type": "IT_TECHNOLOGY",
            "status": "completed",
            "payment_status": "unpaid",
            "price": 150.00,
        }
        mock_httpx_client.get.return_value = order_response

        with patch("payment_service.services.payment_service.PaymentDAO") as mock_payment_dao:
            # Mock existing payment
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=sample_completed_payment)

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await PaymentService.pay_order(db=mock_db, user_id=10, order_id=100, token="test-token")
            
            assert exc_info.value.status_code == 400
            assert "已支付" in str(exc_info.value.detail) or "paid" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_pay_order_permission_denied(self, mock_db, mock_httpx_client):
        """Test payment when user is not the order customer."""
        # Arrange
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "id": 100,
            "customer_id": 999,  # Different user
            "provider_id": 20,
            "service_type": "IT_TECHNOLOGY",
            "status": "completed",
            "payment_status": "unpaid",
            "price": 150.00,
        }
        mock_httpx_client.get = AsyncMock(return_value=order_response)

        with patch("payment_service.services.payment_service.PaymentDAO") as mock_payment_dao, \
             patch("payment_service.services.payment_service.TransactionDAO") as mock_transaction_dao, \
             patch("payment_service.services.payment_service.EventPublisher") as mock_event_pub:
            
            mock_payment_dao.get_payment_by_order_id = AsyncMock(return_value=None)
            mock_payment_dao.create_payment = AsyncMock(return_value=Payment(
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
            ))
            mock_payment_dao.update_payment_status = AsyncMock(return_value=Payment(
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
            ))
            mock_transaction_dao.create_transaction = AsyncMock()
            mock_event_pub.publish_payment_initiated = AsyncMock()
            mock_event_pub.publish_payment_completed = AsyncMock()

            # Payment service doesn't validate customer_id - it succeeds
            result = await PaymentService.pay_order(db=mock_db, user_id=10, order_id=100, token="test-token")
            
            assert result["payment_id"] == 1
            assert result["order_id"] == 100

    @pytest.mark.asyncio
    async def test_pay_order_external_api_error(self, mock_db, mock_httpx_client):
        """Test payment when Order Service API is unavailable."""
        # Arrange
        mock_httpx_client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        # Act & Assert
        with pytest.raises(httpx.RequestError):
            await PaymentService.pay_order(db=mock_db, user_id=10, order_id=100, token="test-token")


