import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )

    account_type = Column(String, nullable=False)
    currency = Column(String, nullable=False)

    balance = Column(Numeric(14, 2), default=0)

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")