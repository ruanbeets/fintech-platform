from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly/{user_id}")
def monthly_report(user_id: UUID, db: Session = Depends(get_db)):

    return ReportsService.monthly_report(db, user_id)


@router.get("/category/{user_id}")
def category_report(user_id: UUID, db: Session = Depends(get_db)):

    return ReportsService.category_report(db, user_id)