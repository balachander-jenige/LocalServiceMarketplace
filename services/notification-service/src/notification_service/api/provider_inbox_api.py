from fastapi import APIRouter, Depends

from ..core.dependencies import get_current_user_id
from ..core.mongodb import get_database
from ..dto.notification_dto import NotificationItem, NotificationListResponse
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/provider/inbox", tags=["provider-inbox"])


@router.get("/", response_model=NotificationListResponse)
async def get_provider_inbox(current_user_id: int = Depends(get_current_user_id), db=Depends(get_database)):
    """GetProviderInbox"""
    service = NotificationService(db)
    notifications = await service.get_provider_inbox(current_user_id)

    items = [
        NotificationItem(
            provider_id=n.provider_id,
            order_id=n.order_id,
            message=n.message,
            created_at=n.created_at.isoformat(),
            is_read=n.is_read,
        )
        for n in notifications
    ]

    return NotificationListResponse(items=items, total=len(items))
