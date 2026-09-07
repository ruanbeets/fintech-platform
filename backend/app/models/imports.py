"""Import provenance and anonymous demo ownership; no changes to the transaction table."""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base


class DemoSession(Base):
    __tablename__ = "demo_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_hash = Column(String(64), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class ImportBatch(Base):
    __tablename__ = "import_batches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("demo_sessions.id"), nullable=False, index=True)
    source_file = Column(String(160), nullable=False)
    file_type = Column(String(12), nullable=False)
    tables = Column(JSON, nullable=True)
    review = Column(JSON, nullable=True)
    review_id = Column(String(64), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    expires_at = Column(DateTime, nullable=False)
    result = Column(JSON, nullable=True)


class ImportedTransaction(Base):
    __tablename__ = "imported_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("demo_sessions.id"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("import_batches.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    fingerprint = Column(String(64), nullable=False)
    source_row = Column(Integer, nullable=False)
    balance_optional = Column(String(40), nullable=True)
    __table_args__ = (UniqueConstraint("session_id", "fingerprint", name="uq_import_fingerprint"),)
