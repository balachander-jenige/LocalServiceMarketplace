from sqlalchemy import Column, BigInteger, String, Enum, DECIMAL, TIMESTAMP, Text
from datetime import datetime, UTC
import enum
from ..core.database import Base

class TransactionType(enum.Enum):
    recharge = "recharge"        # 充值
    payment = "payment"          # 支付
    refund = "refund"            # 退款
    withdrawal = "withdrawal"    # 提现（未实现）

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    balance_before = Column(DECIMAL(10, 2), nullable=False)  # 交易前余额
    balance_after = Column(DECIMAL(10, 2), nullable=False)   # 交易后余额
    reference_id = Column(BigInteger)  # 关联订单/支付ID
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(UTC))