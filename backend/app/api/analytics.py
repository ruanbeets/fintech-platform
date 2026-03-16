from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/spending/{user_id}")
def spending_by_category(user_id: UUID, db: Session = Depends(get_db)):

    return AnalyticsService.spending_by_category(db, user_id)


@router.get("/monthly/{user_id}")
def monthly_spending(user_id: UUID, db: Session = Depends(get_db)):

    return AnalyticsService.monthly_spending(db, user_id)


@router.get("/cashflow/{user_id}")
def cashflow(user_id: UUID, db: Session = Depends(get_db)):

    return AnalyticsService.cashflow_summary(db, user_id)


@router.get("/forecast/{user_id}")
def forecast(user_id: UUID, db: Session = Depends(get_db)):

    return AnalyticsService.balance_forecast(db, user_id)