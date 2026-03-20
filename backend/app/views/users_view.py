from fastapi import APIRouter, HTTPException
from app.viewmodels.users_vm import UsersViewModel

router = APIRouter(prefix="/users")


@router.post("/")
def create_user(data: dict):
    if "email" not in data or "password_hash" not in data:
        raise HTTPException(400, "email and password_hash required")

    if "@" not in data["email"]:
        raise HTTPException(400, "invalid email")

    return UsersViewModel.create_user(data)


@router.get("/")
def get_users():
    return UsersViewModel.get_users()


@router.get("/{user_id}")
def get_user(user_id: str):
    user = UsersViewModel.get_user(user_id)
    if not user:
        raise HTTPException(404, "user not found")
    return user


@router.put("/{user_id}")
def update_user(user_id: str, data: dict):
    if "email" in data and "@" not in data["email"]:
        raise HTTPException(400, "invalid email")

    user = UsersViewModel.update_user(user_id, data)
    if not user:
        raise HTTPException(404, "user not found")

    return user


@router.delete("/{user_id}")
def delete_user(user_id: str):
    success = UsersViewModel.delete_user(user_id)
    if not success:
        raise HTTPException(404, "user not found")

    return {"message": "deleted"}