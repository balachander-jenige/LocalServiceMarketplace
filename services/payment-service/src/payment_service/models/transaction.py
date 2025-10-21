from sqlalchemy import Column, BigInteger, String, Enum, DECIMAL, TIMESTAMP, Text
from datetime import datetime, UTC
import enum
from ..core.database import Base

class TransactionType(enum.Enum):
    payment = "payment"  # 支付
    refund = "refund"    # 退款

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    transaction_type = Column(
        Enum(TransactionType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )
    amount = Column(DECIMAL(10, 2), nullable=False)
    reference_id = Column(BigInteger)  # 关联订单/支付ID
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC))