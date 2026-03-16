from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.audit_repository import AuditRepository


class AuditService:

    @staticmethod
    def log_action(db: Session, user_id: UUID | None, action: str, entity: str):

        return AuditRepository.log(
            db=db,
            user_id=user_id,
            action=action,
            entity=entity
        )


    @staticmethod
    def get_audit_logs(db: Session):

        return AuditRepository.get_all(db)