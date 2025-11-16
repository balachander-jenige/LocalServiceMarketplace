from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.security import HTTPAuthorizationCredentials

from ..clients import auth_client, notification_client, order_client, payment_client, review_client, user_client
from ..dto.response_dto import ApiResponse
from .middleware import apply_rate_limit, get_token_from_request, security, verify_admin_token, verify_auth_token

router = APIRouter()


# ==================== Auth Routes ====================
@router.post("/auth/register", response_model=ApiResponse)
async def register(data: Dict[str, Any] = Body(...)):
    """User Registration"""
    result = await auth_client.register(data)
    return ApiResponse(success=True, data=result, message="Registration successful")


@router.post("/auth/admin/register", response_model=ApiResponse)
async def register_admin(data: Dict[str, Any] = Body(...)):
    """AdminRegistration"""
    result = await auth_client.register_admin(data)
    return ApiResponse(success=True, data=result, message="Admin registration successful")


@router.post("/auth/login", response_model=ApiResponse)
async def login(data: Dict[str, Any] = Body(...)):
    """User Login"""
    result = await auth_client.login(data)
    return ApiResponse(success=True, data=result, message="Login successful")


@router.get("/auth/me", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get Current User"""
    await verify_auth_token(credentials)
    result = await auth_client.get_current_user(credentials.credentials)
    return ApiResponse(success=True, data=result)


# ==================== User Routes - Customer ====================
@router.get("/customer/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCustomerProfile"""
    await verify_auth_token(credentials)
    result = await user_client.get_customer_profile(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.put("/customer/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def update_customer_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """UpdateCustomerProfile"""
    await verify_auth_token(credentials)
    result = await user_client.update_customer_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Customer profile updated")


@router.post("/customer/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def create_customer_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """CreateCustomerProfile"""
    await verify_auth_token(credentials)
    result = await user_client.create_customer_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Customer profile created")


# ==================== User Routes - Provider ====================
@router.get("/provider/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetProviderProfile"""
    await verify_auth_token(credentials)
    result = await user_client.get_provider_profile(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.put("/provider/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def update_provider_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """UpdateProviderProfile"""
    await verify_auth_token(credentials)
    result = await user_client.update_provider_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Provider profile updated")


@router.post("/provider/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def create_provider_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """CreateProviderProfile"""
    await verify_auth_token(credentials)
    result = await user_client.create_provider_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Provider profile created")


# ==================== Customer Order Routes ====================
@router.post("/customer/orders/publish", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def publish_order(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """CustomerPublishOrder"""
    await verify_auth_token(credentials)
    result = await order_client.publish_order(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order published")


@router.get("/customer/orders", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_orders(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCustomerOrderList（进行中）"""
    await verify_auth_token(credentials)
    result = await order_client.get_customer_orders(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/customer/orders/my/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_order_detail(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCustomerOrderDetails"""
    await verify_auth_token(credentials)
    result = await order_client.get_customer_order_detail(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/customer/orders/history", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_order_history(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCustomerOrder历史"""
    await verify_auth_token(credentials)
    result = await order_client.get_customer_order_history(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.post("/customer/orders/cancel/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def cancel_order(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """CustomerCancel Order"""
    await verify_auth_token(credentials)
    result = await order_client.cancel_order(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Order cancelled")


# ==================== Provider Order Routes ====================
@router.get("/provider/orders/available", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_available_orders(
    location: Optional[str] = Query(
        default=None, description="Filter by location: NORTH, SOUTH, EAST, WEST, MID"
    ),
    service_type: Optional[str] = Query(
        default=None,
        description="Filter by service type: cleaning_repair, it_technology, education_training, life_health, design_consulting, other",
    ),
    min_price: Optional[float] = Query(default=None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(default=None, ge=0, description="Maximum price filter"),
    keyword: Optional[str] = Query(default=None, description="Search keyword in title or description"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """GetCan接单List - 支持By地点、Service类型、价格范围And关键词筛选"""
    await verify_auth_token(credentials)
    result = await order_client.get_available_orders(
        token=credentials.credentials,
        location=location,
        service_type=service_type,
        min_price=min_price,
        max_price=max_price,
        keyword=keyword,
    )
    return ApiResponse(success=True, data=result)


@router.get(
    "/provider/orders/available/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)]
)
async def get_available_order_detail(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCan接单Order的Details"""
    await verify_auth_token(credentials)
    result = await order_client.get_available_order_detail(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.post("/provider/orders/accept/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def accept_order(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Provider接单"""
    await verify_auth_token(credentials)
    result = await order_client.accept_order(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Order accepted")


@router.post("/provider/orders/status/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def update_order_status(
    order_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update Order Status"""
    await verify_auth_token(credentials)
    result = await order_client.update_order_status(order_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order status updated")


@router.get("/provider/orders/my/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_order_detail(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetProviderOrderDetails"""
    await verify_auth_token(credentials)
    result = await order_client.get_provider_order_detail(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/provider/orders/history", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_order_history(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetProviderOrder历史"""
    await verify_auth_token(credentials)
    result = await order_client.get_provider_order_history(credentials.credentials)
    return ApiResponse(success=True, data=result)


# ==================== Admin Order Routes ====================
@router.get("/admin/orders", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_all_orders(
    status: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """AdminGet All Orders（CanByStatusFilter）"""
    await verify_admin_token(credentials)
    result = await order_client.get_all_orders(credentials.credentials, status)
    return ApiResponse(success=True, data=result)


@router.get("/admin/orders/pending-review", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_pending_review_orders(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """AdminGet待审核OrderList"""
    await verify_admin_token(credentials)
    result = await order_client.get_pending_review_orders(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/admin/orders/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_order_detail(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """AdminGet Order Details"""
    await verify_admin_token(credentials)
    result = await order_client.get_order_detail_admin(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.post("/admin/orders/{order_id}/approve", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_approve_order(
    order_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Admin审批Order（Approve/Reject）"""
    await verify_admin_token(credentials)
    result = await order_client.approve_order(order_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order approval processed")


@router.put("/admin/orders/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_update_order(
    order_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """AdminUpdateOrderInformation"""
    await verify_admin_token(credentials)
    result = await order_client.update_order_admin(order_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order updated")


@router.delete("/admin/orders/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_delete_order(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """AdminDeleteOrder"""
    await verify_admin_token(credentials)
    result = await order_client.delete_order_admin(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Order deleted")


# ==================== Admin User Routes ====================
@router.get("/admin/users", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_all_users(
    role_id: Optional[int] = None, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """AdminGetAllUser（CanByRoleFilter）"""
    await verify_admin_token(credentials)
    result = await user_client.get_all_users(credentials.credentials, role_id)
    return ApiResponse(success=True, data=result)


@router.get("/admin/users/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_user_detail(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """AdminGet User Details"""
    await verify_admin_token(credentials)
    result = await user_client.get_user_detail_admin(user_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.put("/admin/users/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_update_user(
    user_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """AdminUpdate User Information"""
    await verify_admin_token(credentials)
    result = await user_client.update_user_admin(user_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="User updated")


@router.delete("/admin/users/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_delete_user(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """AdminDelete User"""
    await verify_admin_token(credentials)
    result = await user_client.delete_user_admin(user_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="User deleted")


# ==================== Payment Routes ====================
@router.post("/customer/payments/pay", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def pay_order(data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """CustomerPaymentOrder（MockPayment）"""
    await verify_auth_token(credentials)
    result = await payment_client.pay_order(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Payment successful")


# ==================== Review Routes ====================
@router.post("/reviews", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def create_review(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create评价"""
    await verify_auth_token(credentials)
    result = await review_client.create_review(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Review created")


@router.get("/reviews/provider/me/rating", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_my_provider_rating(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCurrent Provider 的Rating（需Authentication）"""
    await verify_auth_token(credentials)
    result = await review_client.get_my_provider_rating(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/reviews/provider/me/reviews", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_my_provider_reviews(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCurrent Provider 的All评价（需Authentication）"""
    await verify_auth_token(credentials)
    result = await review_client.get_my_provider_reviews(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/reviews/provider/{provider_id}/rating", response_model=ApiResponse)
async def get_provider_rating(provider_id: int):
    """GetProviderRating（公开接口）"""
    result = await review_client.get_provider_rating(provider_id)
    return ApiResponse(success=True, data=result)


@router.get("/reviews/provider/{provider_id}", response_model=ApiResponse)
async def get_provider_reviews(provider_id: int):
    """GetProvider评价List（公开接口）"""
    result = await review_client.get_provider_reviews(provider_id)
    return ApiResponse(success=True, data=result)


# ==================== Notification Routes ====================
@router.get("/customer/inbox", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_inbox(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetCustomerInbox"""
    await verify_auth_token(credentials)
    result = await notification_client.get_customer_inbox(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/provider/inbox", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_inbox(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """GetProviderInbox"""
    await verify_auth_token(credentials)
    result = await notification_client.get_provider_inbox(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.post("/admin/notifications/customer/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_send_customer_notification(
    user_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Admin发送Notification给Customer"""
    await verify_admin_token(credentials)
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    result = await notification_client.admin_send_customer_notification(user_id, message, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Notification sent to customer")


@router.post("/admin/notifications/provider/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_send_provider_notification(
    user_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Admin发送Notification给Provider"""
    await verify_admin_token(credentials)
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    result = await notification_client.admin_send_provider_notification(user_id, message, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Notification sent to provider")
