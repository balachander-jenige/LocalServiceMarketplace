from ...messaging.rabbitmq_client import rabbitmq_client
from ..handlers.user_registered_handler import handle_user_registered


async def start_consuming():
    """Start Consuming Events"""
    await rabbitmq_client.connect()

    # Listen ToUser Registered Event
    await rabbitmq_client.consume_events(
        exchange_name="user_events", routing_key="user.registered", callback=handle_user_registered
    )

    print("✅ Started consuming user events")
