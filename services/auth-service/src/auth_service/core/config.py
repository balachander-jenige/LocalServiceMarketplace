from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database config / 数据库配置
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str = "auth_db"
    DB_PORT: int = 3306
    
    # Database URLs / 数据库连接地址
    LOCAL_DATABASE_URL: str
    DOCKER_DATABASE_URL: str
    AWS_DATABASE_URL: str
    
    # Environment selector / 环境选择器
    USE_DOCKER: bool = False
    
    # JWT config / JWT 配置
    JWT_SECRET_KEY: str = "auth-service-secret-key-2025"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # RabbitMQ config / RabbitMQ 配置
    LOCAL_RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    DOCKER_RABBITMQ_URL: str = "amqp://guest:guest@freelancer-rabbitmq:5672/"
    
    # Service config / 服务配置
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Dynamic database URL selection / 动态数据库 URL 选择
    @property
    def DATABASE_URL(self) -> str:
        """根据环境选择数据库连接 / Select database connection based on environment"""
        if self.USE_DOCKER:
            return self.DOCKER_DATABASE_URL
        else:
            return self.AWS_DATABASE_URL
    
    # Dynamic RabbitMQ URL selection / 动态 RabbitMQ URL 选择
    @property
    def RABBITMQ_URL(self) -> str:
        """根据环境选择 RabbitMQ 连接 / Select RabbitMQ connection based on environment"""
        if self.USE_DOCKER:
            return self.DOCKER_RABBITMQ_URL
        else:
            return self.LOCAL_RABBITMQ_URL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()