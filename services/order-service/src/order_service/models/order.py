from sqlalchemy import Column, BigInteger, String, Text, Enum, DECIMAL, TIMESTAMP
from datetime import datetime, UTC
import enum
from ..core.database import Base

class OrderStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    reviewed = "reviewed"
    cancelled = "cancelled"

class PaymentStatus(enum.Enum):
    unpaid = "unpaid"
    paid = "paid"

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
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    location = Column(Enum(LocationEnum), nullable=False)
    address = Column(String(255))
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid, nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))