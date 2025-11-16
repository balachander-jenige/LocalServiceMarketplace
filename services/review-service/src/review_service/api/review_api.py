from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from ..core.config import settings
from ..core.dependencies import get_current_user_id, security
from ..core.mongodb import get_database
from ..dto.review_dto import CreateReviewRequest, CreateReviewResponse, ProviderRatingResponse
from ..services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=CreateReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: CreateReviewRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user_id: int = Depends(get_current_user_id),
    db=Depends(get_database),
):
    """Create评价（需要Authentication）"""
    service = ReviewService(db)

    # Check该Order是否Already评价
    existing = await service.get_review_by_order(data.order_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This order has already been reviewed")

    # Call Order Service GetOrderInformation
    async with httpx.AsyncClient() as client:
        order_response = await client.get(
            f"{settings.ORDER_SERVICE_URL}/customer/orders/my/{data.order_id}",
            headers={"Authorization": f"Bearer {credentials.credentials}"},
        )

        if order_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or you don't have permission to review this order",
            )

        order = order_response.json()

    # VerifyOrder属于CurrentUser（customer）
    if order["customer_id"] != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only review your own orders")

    # VerifyOrderAlreadyComplete且AlreadyPayment
    if order["status"] != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only review completed orders")

    if order.get("payment_status") != "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only review paid orders")

    # Create评价，使用从OrderGet的 customer_id And provider_id
    review_data = {
        "order_id": data.order_id,
        "customer_id": order["customer_id"],
        "provider_id": order["provider_id"],
        "stars": data.stars,
        "content": data.content,
    }

    review = await service.create_review(review_data)
    return CreateReviewResponse(
        review_id=str(review.order_id),
        order_id=review.order_id,
        stars=review.stars,
        content=review.content,
        message="Review created successfully.",
    )


@router.get("/provider/me/rating", response_model=ProviderRatingResponse)
async def get_my_provider_rating(current_user_id: int = Depends(get_current_user_id), db=Depends(get_database)):
    """GetCurrent Provider 的Rating（需要Authentication）"""
    service = ReviewService(db)
    rating = await service.get_provider_rating(current_user_id)
    return ProviderRatingResponse(
        provider_id=rating.provider_id, average_rating=rating.average_rating, total_reviews=rating.total_reviews
    )


@router.get("/provider/me/reviews", response_model=List[dict])
async def get_my_provider_reviews(current_user_id: int = Depends(get_current_user_id), db=Depends(get_database)):
    """GetCurrent Provider 的All评价（需要Authentication）"""
    service = ReviewService(db)
    reviews = await service.get_reviews_for_provider(current_user_id)
    return [
        {
            "order_id": r.order_id,
            "customer_id": r.customer_id,
            "stars": r.stars,
            "content": r.content,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]


@router.get("/provider/{provider_id}/rating", response_model=ProviderRatingResponse)
async def get_provider_rating(provider_id: int, db=Depends(get_database)):
    """GetProviderRating（公开接口）"""
    service = ReviewService(db)
    rating = await service.get_provider_rating(provider_id)
    return ProviderRatingResponse(
        provider_id=rating.provider_id, average_rating=rating.average_rating, total_reviews=rating.total_reviews
    )


@router.get("/provider/{provider_id}", response_model=List[dict])
async def get_provider_reviews(provider_id: int, db=Depends(get_database)):
    """GetProvider的All评价（公开接口）"""
    service = ReviewService(db)
    reviews = await service.get_reviews_for_provider(provider_id)
    return [
        {
            "order_id": r.order_id,
            "customer_id": r.customer_id,
            "stars": r.stars,
            "content": r.content,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]


@router.get("/order/{order_id}", response_model=dict)
async def get_order_review(order_id: int, db=Depends(get_database)):
    """ByOrderIDGet评价（公开接口）"""
    service = ReviewService(db)
    review = await service.get_review_by_order(order_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found for this order")
    return {
        "order_id": review.order_id,
        "customer_id": review.customer_id,
        "provider_id": review.provider_id,
        "stars": review.stars,
        "content": review.content,
        "created_at": review.created_at.isoformat(),
    }
