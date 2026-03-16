from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.budgets_service import BudgetsService

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/")
def create_budget(user_id: UUID, category_id: UUID, limit: float, db: Session = Depends(get_db)):

    return BudgetsService.create_budget(db, user_id, category_id, limit)


@router.get("/{user_id}")
def get_user_budgets(user_id: UUID, db: Session = Depends(get_db)):

    return BudgetsService.get_user_budgets(db, user_id)


@router.get("/status/{user_id}")
def check_budget_status(user_id: UUID, db: Session = Depends(get_db)):

    return BudgetsService.check_budget_status(db, user_id)