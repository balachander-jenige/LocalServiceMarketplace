from sqlalchemy import Column, BigInteger, Enum, DECIMAL, TIMESTAMP, Text
from datetime import datetime, UTC
import enum
from ..core.database import Base

class RefundStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    rejected = "rejected"

class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    payment_id = Column(BigInteger, nullable=False, index=True)
    order_id = Column(BigInteger, nullable=False, index=True)
    customer_id = Column(BigInteger, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(RefundStatus), default=RefundStatus.pending, nullable=False)
    reason = Column(Text)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))