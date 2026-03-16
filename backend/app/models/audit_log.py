from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.database.base import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    action = Column(String, nullable=False)
    entity = Column(String)

    user_id = Column(UUID(as_uuid=True))

    timestamp = Column(DateTime, default=datetime.utcnow)