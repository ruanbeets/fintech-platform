from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.services.users_service import UsersService
from app.schemas.user_schema import UserCreate, UserLogin
from app.schemas.auth_schema import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    try:

        created_user = UsersService.register_user(
            db,
            user.email,
            user.password
        )

        return created_user

    except ValueError as e:

        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):

    try:

        token = UsersService.authenticate_user(
            db,
            user.email,
            user.password
        )

        return token

    except ValueError as e:

        raise HTTPException(status_code=401, detail=str(e))