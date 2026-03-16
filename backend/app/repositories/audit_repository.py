from sqlalchemy.orm import Session
from uuid import UUID

from app.models.audit_log import AuditLog


class AuditRepository:

    @staticmethod
    def log(db: Session, user_id: UUID | None, action: str, entity: str):

        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
        )

        db.add(audit)
        db.commit()

        return audit

    @staticmethod
    def get_all(db: Session):

        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()