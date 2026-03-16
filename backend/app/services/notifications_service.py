from sqlalchemy.orm import Session
from uuid import UUID

from app.models.notification import Notification


class NotificationsService:

    @staticmethod
    def create_notification(db: Session, user_id: UUID, message: str):

        notification = Notification(
            user_id=user_id,
            message=message
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification


    @staticmethod
    def get_user_notifications(db: Session, user_id: UUID):

        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )


    @staticmethod
    def mark_as_read(db: Session, notification_id: UUID):

        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            raise ValueError("Notification not found")

        notification.read = True

        db.commit()

        return notification