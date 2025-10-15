from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB config
    MONGODB_URL: str
    
    # RabbitMQ config
    RABBITMQ_URL: str
    
    # Auth Service URL
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    
    # Service config
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8002
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()