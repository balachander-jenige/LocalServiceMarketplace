from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, UTC
from ..dao.review_dao import ReviewDAO
from ..dao.rating_dao import RatingDAO
from ..models.review import Review
from ..models.rating import ProviderRating
from ..domain.events.review_created import ReviewCreatedEvent
from ..domain.events.rating_updated import RatingUpdatedEvent
from ..events.publishers.event_publisher import EventPublisher

class ReviewService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.review_dao = ReviewDAO(db)
        self.rating_dao = RatingDAO(db)

    async def create_review(self, review_data: dict):
        """创建评价并更新服务商评分"""
        review = Review(**review_data)
        created_review = await self.review_dao.create(review)
        
        # 发布评价创建事件
        review_event = ReviewCreatedEvent(
            review_id=str(created_review.order_id),  # MongoDB没有自增ID，用order_id代替
            order_id=created_review.order_id,
            customer_id=created_review.customer_id,
            provider_id=created_review.provider_id,
            stars=created_review.stars,
            content=created_review.content or "",
            timestamp=datetime.now(UTC)
        )
        await EventPublisher.publish_review_created(review_event)
        
        # 更新服务商评分
        reviews = await self.review_dao.get_reviews_for_provider(review.provider_id)
        total_reviews = len(reviews)
        average_rating = sum(r.stars for r in reviews) / total_reviews if total_reviews > 0 else 5.0
        
        await self.rating_dao.upsert_rating(review.provider_id, average_rating, total_reviews)
        
        # 发布评分更新事件
        rating_event = RatingUpdatedEvent(
            provider_id=review.provider_id,
            average_rating=average_rating,
            total_reviews=total_reviews,
            timestamp=datetime.now(UTC)
        )
        await EventPublisher.publish_rating_updated(rating_event)
        
        return created_review

    async def get_provider_rating(self, provider_id: int) -> ProviderRating:
        """获取服务商评分"""
        rating = await self.rating_dao.get_by_provider_id(provider_id)
        if not rating:
            return ProviderRating(provider_id=provider_id, average_rating=5.0, total_reviews=0)
        return rating
    
    async def get_reviews_for_provider(self, provider_id: int):
        """获取服务商的所有评价"""
        return await self.review_dao.get_reviews_for_provider(provider_id)
    
    async def get_review_by_order(self, order_id: int):
        """根据订单ID获取评价"""
        return await self.review_dao.get_by_order_id(order_id)