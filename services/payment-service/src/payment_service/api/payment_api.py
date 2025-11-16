from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.dependencies import get_current_user_id, security
from ..dto.payment_dto import PayOrderRequest, PayOrderResponse
from ..services.payment_service import PaymentService

router = APIRouter(prefix="/customer/payments", tags=["Payments"])


@router.post("/pay", response_model=PayOrderResponse)
async def pay_order(
    data: PayOrderRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CustomerPaymentOrder（MockPayment）"""
    result = await PaymentService.pay_order(db, user_id, data.order_id, credentials.credentials)

    return PayOrderResponse(
        payment_id=result["payment_id"], order_id=result["order_id"], amount=result["amount"], message=result["message"]
    )
