from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from datetime import datetime, UTC
from decimal import Decimal

from ..models.transaction import Transaction, TransactionType

class TransactionDAO:
    """交易记录数据访问对象"""
    
    @staticmethod
    async def create_transaction(
        db: AsyncSession,
        user_id: int,
        transaction_type: TransactionType,
        amount: float,
        reference_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Transaction:
        """创建交易记录（简化版，不含余额信息）"""
        transaction = Transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=Decimal(str(amount)),
            reference_id=reference_id,
            description=description,
            created_at=datetime.now(UTC)
        )
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    @staticmethod
    async def get_user_transactions(
        db: AsyncSession,
        user_id: int,
        limit: int = 50
    ) -> List[Transaction]:
        """获取用户的交易记录"""
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())