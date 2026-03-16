from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.users_service import UsersService
from app.schemas.user_schema import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, db: Session = Depends(get_db)):

    try:

        return UsersService.get_user(db, user_id)

    except ValueError as e:

        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}")
def delete_user(user_id: UUID, db: Session = Depends(get_db)):

    try:

        return UsersService.delete_user(db, user_id)

    except ValueError as e:

        raise HTTPException(status_code=404, detail=str(e))