from fastapi import APIRouter
from app.viewmodels.dashboard_vm import DashboardViewModel

router = APIRouter(prefix="/dashboard")


@router.get("/{user_id}")
def get_dashboard(user_id: str):
    return DashboardViewModel.get_summary(user_id)