from fastapi import APIRouter, Depends
from ..core.mongodb import get_database
from ..core.dependencies import get_current_user_id
from ..dto.notification_dto import NotificationItem, NotificationListResponse
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/customer/inbox", tags=["customer-inbox"])

@router.get("/", response_model=NotificationListResponse)
async def get_customer_inbox(
    current_user_id: int = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """获取客户收件箱"""
    service = NotificationService(db)
    notifications = await service.get_customer_inbox(current_user_id)
    
    items = [
        NotificationItem(
            customer_id=n.customer_id,
            order_id=n.order_id,
            message=n.message,
            created_at=n.created_at.isoformat(),
            is_read=n.is_read
        )
        for n in notifications
    ]
    
    return NotificationListResponse(items=items, total=len(items))