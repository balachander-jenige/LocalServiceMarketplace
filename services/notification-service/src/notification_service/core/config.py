from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    REDIS_URL: str
    RABBITMQ_URL: str
    AUTH_SERVICE_URL: str
    USER_SERVICE_URL: str
    ORDER_SERVICE_URL: str
    PAYMENT_SERVICE_URL: str
    REVIEW_SERVICE_URL: str
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8006
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()