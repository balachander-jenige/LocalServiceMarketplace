from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    RABBITMQ_URL: str
    AUTH_SERVICE_URL: str
    ORDER_SERVICE_URL: str
    USER_SERVICE_URL: str
    SERVICE_NAME: str = "review-service"
    SERVICE_PORT: int = 8005
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()