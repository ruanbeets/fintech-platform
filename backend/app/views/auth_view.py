from fastapi import APIRouter, HTTPException
from app.viewmodels.auth_vm import AuthViewModel

router = APIRouter(prefix="/auth")


@router.post("/register")
def register(data: dict):
    if "email" not in data or "password" not in data:
        raise HTTPException(400, "email and password required")

    data["password_hash"] = data["password"]  # placeholder
    return AuthViewModel.register(data)


@router.post("/login")
def login(data: dict):
    if "email" not in data or "password" not in data:
        raise HTTPException(400, "email and password required")

    user = AuthViewModel.login(data)

    if not user:
        raise HTTPException(401, "invalid credentials")

    return user