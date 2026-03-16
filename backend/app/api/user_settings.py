from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/{user_id}")
def get_settings(user_id: UUID, db: Session = Depends(get_db)):

    return SettingsService.get_user_settings(db, user_id)


@router.patch("/{user_id}/email")
def update_email(user_id: UUID, email: str, db: Session = Depends(get_db)):

    return SettingsService.update_user_email(db, user_id, email)