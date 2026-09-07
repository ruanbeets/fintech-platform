from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings
from app.schemas.dashboard import DashboardSummary
from app.viewmodels.dashboard_vm import DashboardViewModel

router = APIRouter(prefix="/dashboard")
MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


def summary(user_id, month, currency, demo=False):
    try:
        return DashboardViewModel.get_summary(user_id, month=month, currency=currency, demo=demo)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/demo", response_model=DashboardSummary)
def get_demo(month: str | None = Query(None, pattern=MONTH_PATTERN),
             currency: str | None = Query(None, pattern=r"^[A-Za-z]{3}$")):
    if not (settings.local_demo or settings.demo_mode):
        raise HTTPException(404, "Local demo is disabled")
    from scripts.seed_demo import DEMO_USER_ID
    return summary(DEMO_USER_ID, month, currency, demo=True)


@router.get("/{user_id}", response_model=DashboardSummary)
def get_dashboard(user_id: UUID, month: str | None = Query(None, pattern=MONTH_PATTERN),
                  currency: str | None = Query(None, pattern=r"^[A-Za-z]{3}$")):
    return summary(user_id, month, currency)
