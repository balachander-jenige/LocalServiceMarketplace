from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..dto.refund_dto import RefundRequest, RefundResponse
from ..services.refund_service import RefundService

router = APIRouter(prefix="/customer/refunds", tags=["Refunds"])

@router.post("/", response_model=RefundResponse)
async def process_refund(
    data: RefundRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """申请退款"""
    result = await RefundService.process_refund(
        db, user_id, data.order_id, data.reason
    )
    
    return RefundResponse(
        refund_id=result["refund_id"],
        order_id=result["order_id"],
        amount=result["amount"],
        status=result["status"],
        message=result["message"]
    )