from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service URLs
    AUTH_SERVICE_URL: str
    USER_SERVICE_URL: str
    ORDER_SERVICE_URL: str
    PAYMENT_SERVICE_URL: str
    REVIEW_SERVICE_URL: str
    NOTIFICATION_SERVICE_URL: str

    # Gateway configuration
    SERVICE_NAME: str = "gateway-service"
    SERVICE_PORT: int = 8080
    LOG_LEVEL: str = "INFO"

    # JWT configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
