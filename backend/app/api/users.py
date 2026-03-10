from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.users_service import (
    create_new_user,
    list_users
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return create_new_user(db, payload.email)


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return list_users(db)