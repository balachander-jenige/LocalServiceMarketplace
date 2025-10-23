from .auth_client import auth_client
from .user_client import user_client
from .order_client import order_client
from .payment_client import payment_client
from .review_client import review_client
from .notification_client import notification_client

__all__ = [
    "auth_client",
    "user_client",
    "order_client",
    "payment_client",
    "review_client",
    "notification_client"
]