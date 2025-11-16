import enum
from datetime import UTC, datetime

from sqlalchemy import DECIMAL, TIMESTAMP, BigInteger, Column, Enum, Integer, String

from ..core.database import Base


class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class PaymentMethod(enum.Enum):
    simulated = "simulated"  # MockPayment（简化后的Payment方式）


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, nullable=False, index=True)
    customer_id = Column(BigInteger, nullable=False, index=True)
    provider_id = Column(BigInteger, nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(
        Enum(PaymentMethod, values_callable=lambda obj: [e.value for e in obj]),
        default=PaymentMethod.simulated,
        nullable=False,
    )
    status = Column(
        Enum(PaymentStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=PaymentStatus.pending,
        nullable=False,
    )
    transaction_id = Column(String(255), unique=True)  # Transaction流水号
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
