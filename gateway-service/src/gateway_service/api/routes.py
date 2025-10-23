from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from ..clients import auth_client, notification_client, order_client, payment_client, review_client, user_client
from ..dto.response_dto import ApiResponse
from .middleware import apply_rate_limit, get_token_from_request, security, verify_admin_token, verify_auth_token

router = APIRouter()


# ==================== Auth Routes ====================
@router.post("/auth/register", response_model=ApiResponse)
async def register(data: Dict[str, Any] = Body(...)):
    """用户注册"""
    result = await auth_client.register(data)
    return ApiResponse(success=True, data=result, message="Registration successful")


@router.post("/auth/admin/register", response_model=ApiResponse)
async def register_admin(data: Dict[str, Any] = Body(...)):
    """管理员注册"""
    result = await auth_client.register_admin(data)
    return ApiResponse(success=True, data=result, message="Admin registration successful")


@router.post("/auth/login", response_model=ApiResponse)
async def login(data: Dict[str, Any] = Body(...)):
    """用户登录"""
    result = await auth_client.login(data)
    return ApiResponse(success=True, data=result, message="Login successful")


@router.get("/auth/me", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    await verify_auth_token(credentials)
    result = await auth_client.get_current_user(credentials.credentials)
    return ApiResponse(success=True, data=result)


# ==================== User Routes - Customer ====================
@router.get("/customer/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取客户资料"""
    await verify_auth_token(credentials)
    result = await user_client.get_customer_profile(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.put("/customer/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def update_customer_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """更新客户资料"""
    await verify_auth_token(credentials)
    result = await user_client.update_customer_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Customer profile updated")


@router.post("/customer/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def create_customer_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """创建客户资料"""
    await verify_auth_token(credentials)
    result = await user_client.create_customer_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Customer profile created")


# ==================== User Routes - Provider ====================
@router.get("/provider/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取服务商资料"""
    await verify_auth_token(credentials)
    result = await user_client.get_provider_profile(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.put("/provider/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def update_provider_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """更新服务商资料"""
    await verify_auth_token(credentials)
    result = await user_client.update_provider_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Provider profile updated")


@router.post("/provider/profile", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def create_provider_profile(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """创建服务商资料"""
    await verify_auth_token(credentials)
    result = await user_client.create_provider_profile(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Provider profile created")


# ==================== Customer Order Routes ====================
@router.post("/customer/orders/publish", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def publish_order(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """客户发布订单"""
    await verify_auth_token(credentials)
    result = await order_client.publish_order(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order published")


@router.get("/customer/orders", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_orders(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取客户订单列表（进行中）"""
    await verify_auth_token(credentials)
    result = await order_client.get_customer_orders(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/customer/orders/my/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_order_detail(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取客户订单详情"""
    await verify_auth_token(credentials)
    result = await order_client.get_customer_order_detail(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/customer/orders/history", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_order_history(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取客户订单历史"""
    await verify_auth_token(credentials)
    result = await order_client.get_customer_order_history(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.post("/customer/orders/cancel/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def cancel_order(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """客户取消订单"""
    await verify_auth_token(credentials)
    result = await order_client.cancel_order(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Order cancelled")


# ==================== Provider Order Routes ====================
@router.get("/provider/orders/available", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_available_orders(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取可接单列表"""
    await verify_auth_token(credentials)
    result = await order_client.get_available_orders(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.post("/provider/orders/accept/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def accept_order(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """服务商接单"""
    await verify_auth_token(credentials)
    result = await order_client.accept_order(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Order accepted")


@router.post("/provider/orders/status/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def update_order_status(
    order_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """更新订单状态"""
    await verify_auth_token(credentials)
    result = await order_client.update_order_status(order_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order status updated")


@router.get("/provider/orders/my/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_order_detail(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取服务商订单详情"""
    await verify_auth_token(credentials)
    result = await order_client.get_provider_order_detail(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/provider/orders/history", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_order_history(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取服务商订单历史"""
    await verify_auth_token(credentials)
    result = await order_client.get_provider_order_history(credentials.credentials)
    return ApiResponse(success=True, data=result)


# ==================== Admin Order Routes ====================
@router.get("/admin/orders", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_all_orders(
    status: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """管理员获取所有订单（可按状态过滤）"""
    await verify_admin_token(credentials)
    result = await order_client.get_all_orders(credentials.credentials, status)
    return ApiResponse(success=True, data=result)


@router.get("/admin/orders/pending-review", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_pending_review_orders(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """管理员获取待审核订单列表"""
    await verify_admin_token(credentials)
    result = await order_client.get_pending_review_orders(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/admin/orders/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_order_detail(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """管理员获取订单详情"""
    await verify_admin_token(credentials)
    result = await order_client.get_order_detail_admin(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.post("/admin/orders/{order_id}/approve", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_approve_order(
    order_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """管理员审批订单（批准/拒绝）"""
    await verify_admin_token(credentials)
    result = await order_client.approve_order(order_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order approval processed")


@router.put("/admin/orders/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_update_order(
    order_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """管理员更新订单信息"""
    await verify_admin_token(credentials)
    result = await order_client.update_order_admin(order_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Order updated")


@router.delete("/admin/orders/{order_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_delete_order(order_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """管理员删除订单"""
    await verify_admin_token(credentials)
    result = await order_client.delete_order_admin(order_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="Order deleted")


# ==================== Admin User Routes ====================
@router.get("/admin/users", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_all_users(
    role_id: Optional[int] = None, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """管理员获取所有用户（可按角色过滤）"""
    await verify_admin_token(credentials)
    result = await user_client.get_all_users(credentials.credentials, role_id)
    return ApiResponse(success=True, data=result)


@router.get("/admin/users/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_get_user_detail(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """管理员获取用户详情"""
    await verify_admin_token(credentials)
    result = await user_client.get_user_detail_admin(user_id, credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.put("/admin/users/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_update_user(
    user_id: int, data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """管理员更新用户信息"""
    await verify_admin_token(credentials)
    result = await user_client.update_user_admin(user_id, credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="User updated")


@router.delete("/admin/users/{user_id}", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def admin_delete_user(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """管理员删除用户"""
    await verify_admin_token(credentials)
    result = await user_client.delete_user_admin(user_id, credentials.credentials)
    return ApiResponse(success=True, data=result, message="User deleted")


# ==================== Payment Routes ====================
@router.post("/customer/payments/pay", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def pay_order(data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """客户支付订单（模拟支付）"""
    await verify_auth_token(credentials)
    result = await payment_client.pay_order(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Payment successful")


# ==================== Review Routes ====================
@router.post("/reviews", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def create_review(
    data: Dict[str, Any] = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """创建评价"""
    await verify_auth_token(credentials)
    result = await review_client.create_review(credentials.credentials, data)
    return ApiResponse(success=True, data=result, message="Review created")


@router.get("/reviews/provider/me/rating", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_my_provider_rating(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前 Provider 的评分（需认证）"""
    await verify_auth_token(credentials)
    result = await review_client.get_my_provider_rating(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/reviews/provider/me/reviews", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_my_provider_reviews(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前 Provider 的所有评价（需认证）"""
    await verify_auth_token(credentials)
    result = await review_client.get_my_provider_reviews(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/reviews/provider/{provider_id}/rating", response_model=ApiResponse)
async def get_provider_rating(provider_id: int):
    """获取服务商评分（公开接口）"""
    result = await review_client.get_provider_rating(provider_id)
    return ApiResponse(success=True, data=result)


@router.get("/reviews/provider/{provider_id}", response_model=ApiResponse)
async def get_provider_reviews(provider_id: int):
    """获取服务商评价列表（公开接口）"""
    result = await review_client.get_provider_reviews(provider_id)
    return ApiResponse(success=True, data=result)


# ==================== Notification Routes ====================
@router.get("/customer/inbox", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_customer_inbox(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取客户收件箱"""
    await verify_auth_token(credentials)
    result = await notification_client.get_customer_inbox(credentials.credentials)
    return ApiResponse(success=True, data=result)


@router.get("/provider/inbox", response_model=ApiResponse, dependencies=[Depends(apply_rate_limit)])
async def get_provider_inbox(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取服务商收件箱"""
    await verify_auth_token(credentials)
    result = await notification_client.get_provider_inbox(credentials.credentials)
    return ApiResponse(success=True, data=result)
