from sqlalchemy import Column, String, Numeric, TIMESTAMP, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Numeric(14, 2), nullable=False)
    type = Column(String, nullable=False)  # income | expense | transfer

    category = Column(String, nullable=True)
    merchant = Column(String, nullable=True)
    description = Column(String, nullable=True)

    occurred_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense', 'transfer')",
            name="check_transaction_type"
        ),
    )