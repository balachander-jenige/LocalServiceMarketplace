from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.dependencies import get_current_user_id
from ..core.mongodb import get_database
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/admin/notifications", tags=["admin-notifications"])


class SendNotificationRequest(BaseModel):
    """发送Notification请求"""

    message: str

    class Config:
        json_schema_extra = {"example": {"message": "平台维护通知：系统将于今晚进行维护。"}}


class SendNotificationResponse(BaseModel):
    """发送Notification响应"""

    user_id: int
    message: str


@router.post("/customer/{user_id}", response_model=SendNotificationResponse)
async def send_customer_notification(
    user_id: int, request: SendNotificationRequest, current_user_id: int = Depends(get_current_user_id), db=Depends(get_database)
):
    """Admin发送Notification给Customer"""
    # Note: Gateway 层会VerifyAdminPermission
    service = NotificationService(db)

    # 发送Notification（order_id 为 None 表示平台Notification）
    await service.send_customer_notification(customer_id=user_id, order_id=None, message=request.message)

    return SendNotificationResponse(user_id=user_id, message="Notification sent successfully to customer")


@router.post("/provider/{user_id}", response_model=SendNotificationResponse)
async def send_provider_notification(
    user_id: int, request: SendNotificationRequest, current_user_id: int = Depends(get_current_user_id), db=Depends(get_database)
):
    """Admin发送Notification给Provider"""
    # Note: Gateway 层会VerifyAdminPermission
    service = NotificationService(db)

    # 发送Notification（order_id 为 None 表示平台Notification）
    await service.send_provider_notification(provider_id=user_id, order_id=None, message=request.message)

    return SendNotificationResponse(user_id=user_id, message="Notification sent successfully to provider")
