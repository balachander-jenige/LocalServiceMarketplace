from sqlalchemy import Column, BigInteger, String, Text, Enum, DECIMAL, TIMESTAMP, DateTime
from datetime import datetime, UTC
import enum
from ..core.database import Base

class OrderStatus(enum.Enum):
    pending_review = "pending_review"  # 新增:待审核状态
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    reviewed = "reviewed"
    cancelled = "cancelled"

class PaymentStatus(enum.Enum):
    unpaid = "unpaid"
    paid = "paid"

class ServiceType(enum.Enum):
    """服务类型枚举"""
    CLEANING_REPAIR = "cleaning_repair"  # 清洁与维修
    IT_TECHNOLOGY = "it_technology"  # IT与技术
    EDUCATION_TRAINING = "education_training"  # 教育与培训
    LIFE_HEALTH = "life_health"  # 生活与健康
    DESIGN_CONSULTING = "design_consulting"  # 设计与咨询
    OTHER = "other"  # 其他

class LocationEnum(enum.Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    MID = "MID"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, nullable=False, index=True)
    provider_id = Column(BigInteger, nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    service_type = Column(Enum(ServiceType, values_callable=lambda obj: [e.value for e in obj]), nullable=False, index=True)  # 新增:服务类型
    status = Column(Enum(OrderStatus, values_callable=lambda obj: [e.value for e in obj]), default=OrderStatus.pending_review, nullable=False, index=True)  # 修改默认状态为 pending_review
    price = Column(DECIMAL(10, 2), nullable=False)
    location = Column(Enum(LocationEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    address = Column(String(255))
    service_start_time = Column(DateTime, nullable=True)  # 新增:服务开始时间
    service_end_time = Column(DateTime, nullable=True)  # 新增:服务结束时间
    payment_status = Column(Enum(PaymentStatus, values_callable=lambda obj: [e.value for e in obj]), default=PaymentStatus.unpaid, nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))