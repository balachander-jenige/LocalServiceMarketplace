from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database config
    DATABASE_URL: str
    
    # RabbitMQ config
    RABBITMQ_URL: str
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    USER_SERVICE_URL: str = "http://localhost:8002"
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    
    # Service config
    SERVICE_NAME: str = "payment-service"
    SERVICE_PORT: int = 8004
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()