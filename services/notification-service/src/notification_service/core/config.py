from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB config / MongoDB 配置
    MONGODB_URL: str  # MongoDB Atlas URL
    LOCAL_MONGODB_URL: str = "mongodb://freelancer:Password123@localhost:27017/notification_db"
    DOCKER_MONGODB_URL: str = "mongodb://freelancer:Password123@freelancer-mongodb:27017/notification_db"
    
    # Redis config / Redis 配置
    LOCAL_REDIS_HOST: str = "localhost"
    LOCAL_REDIS_PORT: int = 6379
    LOCAL_REDIS_URL: str = "redis://localhost:6379"
    
    DOCKER_REDIS_HOST: str = "freelancer-redis"
    DOCKER_REDIS_PORT: int = 6379
    DOCKER_REDIS_URL: str = "redis://freelancer-redis:6379"
    
    # Environment selectors / 环境选择器
    USE_LOCAL_MONGODB: bool = False
    USE_DOCKER: bool = False
    
    # RabbitMQ config / RabbitMQ 配置
    LOCAL_RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    DOCKER_RABBITMQ_URL: str = "amqp://guest:guest@freelancer-rabbitmq:5672/"
    
    # Service URLs / 服务地址
    ORDER_SERVICE_URL: str = "http://localhost:8001"
    PAYMENT_SERVICE_URL: str = "http://localhost:8003"
    USER_SERVICE_URL: str = "http://localhost:8002"
    
    # Service config / 服务配置
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8005
    LOG_LEVEL: str = "INFO"
    
    # Dynamic MongoDB URL selection / 动态 MongoDB URL 选择
    @property
    def EFFECTIVE_MONGODB_URL(self) -> str:
        """根据环境选择 MongoDB 连接 / Select MongoDB connection based on environment"""
        if self.USE_LOCAL_MONGODB:
            if self.USE_DOCKER:
                return self.DOCKER_MONGODB_URL
            else:
                return self.LOCAL_MONGODB_URL
        else:
            return self.MONGODB_URL
    
    # Dynamic Redis URL selection / 动态 Redis URL 选择
    @property
    def REDIS_URL(self) -> str:
        """根据环境选择 Redis 连接 / Select Redis connection based on environment"""
        if self.USE_DOCKER:
            return self.DOCKER_REDIS_URL
        else:
            return self.LOCAL_REDIS_URL
    
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