from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database config / 数据库配置
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str = "payment_db"
    DB_PORT: int = 3306
    
    # Database URLs / 数据库连接地址
    LOCAL_DATABASE_URL: str
    DOCKER_DATABASE_URL: str
    AWS_DATABASE_URL: str
    
    # Environment selector / 环境选择器
    USE_DOCKER: bool = False
    
    # RabbitMQ config / RabbitMQ 配置
    LOCAL_RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    DOCKER_RABBITMQ_URL: str = "amqp://guest:guest@freelancer-rabbitmq:5672/"
    
    # Service URLs / 服务地址
    ORDER_SERVICE_URL: str = "http://localhost:8001"
    USER_SERVICE_URL: str = "http://localhost:8002"
    
    # Payment settings / 支付设置
    MIN_RECHARGE_AMOUNT: float = 1.0
    MAX_RECHARGE_AMOUNT: float = 10000.0
    PAYMENT_TIMEOUT_MINUTES: int = 15
    
    # Service config / 服务配置
    SERVICE_NAME: str = "payment-service"
    SERVICE_PORT: int = 8003
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