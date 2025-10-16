from ...messaging.rabbitmq_client import rabbitmq_client
from ...domain.events.review_created import ReviewCreatedEvent
from ...domain.events.rating_updated import RatingUpdatedEvent

class EventPublisher:
    @staticmethod
    async def publish_review_created(event: ReviewCreatedEvent):
        await rabbitmq_client.publish_event(
            exchange_name="review_events",
            routing_key="review.created",
            message=event.model_dump_json()
        )

    @staticmethod
    async def publish_rating_updated(event: RatingUpdatedEvent):
        await rabbitmq_client.publish_event(
            exchange_name="review_events",
            routing_key="rating.updated",
            message=event.model_dump_json()
        )