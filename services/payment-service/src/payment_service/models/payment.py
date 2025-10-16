from sqlalchemy import Column, BigInteger, Integer, String, Enum, DECIMAL, TIMESTAMP
from datetime import datetime, UTC
import enum
from ..core.database import Base

class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class PaymentMethod(enum.Enum):
    balance = "balance"          # 余额支付
    credit_card = "credit_card"  # 信用卡（未实现）
    paypal = "paypal"            # PayPal（未实现）

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, nullable=False, index=True)
    customer_id = Column(BigInteger, nullable=False, index=True)
    provider_id = Column(BigInteger, nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.balance, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    transaction_id = Column(String(255), unique=True)  # 交易流水号
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))