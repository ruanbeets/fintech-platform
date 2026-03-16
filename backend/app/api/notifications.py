from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.notifications_service import NotificationsService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/{user_id}")
def get_notifications(user_id: UUID, db: Session = Depends(get_db)):

    return NotificationsService.get_user_notifications(db, user_id)


@router.post("/")
def create_notification(user_id: UUID, message: str, db: Session = Depends(get_db)):

    return NotificationsService.create_notification(db, user_id, message)


@router.patch("/{notification_id}/read")
def mark_read(notification_id: UUID, db: Session = Depends(get_db)):

    return NotificationsService.mark_as_read(db, notification_id)