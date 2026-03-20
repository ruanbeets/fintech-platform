from fastapi import APIRouter
from app.viewmodels.settings_vm import SettingsViewModel

router = APIRouter(prefix="/settings")


@router.get("/{user_id}")
def get_settings(user_id: str):
    return SettingsViewModel.get_settings(user_id)


@router.put("/{user_id}")
def update_settings(user_id: str, data: dict):
    return SettingsViewModel.update_settings(user_id, data)