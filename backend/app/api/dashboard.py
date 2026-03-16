from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{user_id}")
def get_dashboard(user_id: UUID, db: Session = Depends(get_db)):

    return DashboardService.get_dashboard_summary(db, user_id)