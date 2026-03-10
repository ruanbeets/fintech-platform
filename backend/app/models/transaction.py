import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.account_id"),
        nullable=False
    )

    date = Column(Date, nullable=False)

    amount = Column(Numeric(14, 2), nullable=False)

    balance = Column(Numeric(14, 2), nullable=False)

    category = Column(String)
    description = Column(String)

    # Relationships
    account = relationship("Account", back_populates="transactions")