from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    # JWT config / JWT Configuration
    JWT_SECRET_KEY: str = "auth-service-secret-key-2025"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # RabbitMQ config / RabbitMQ Configuration
    LOCAL_RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    DOCKER_RABBITMQ_URL: str = "amqp://guest:guest@freelancer-rabbitmq:5672/"

    # Service config / ServiceConfiguration
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    @property
    def RABBITMQ_URL(self) -> str:
        # Currently Directly Returns Local RabbitMQ Address
        return self.LOCAL_RABBITMQ_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
