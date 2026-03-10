from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.schemas.account_schema import AccountCreate, AccountResponse
from app.services.accounts_service import (
    create_new_account,
    list_user_accounts
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    return create_new_account(
        db,
        payload.user_id,
        payload.account_type,
        payload.currency
    )


@router.get("/", response_model=list[AccountResponse])
def get_accounts(user_id: UUID, db: Session = Depends(get_db)):
    return list_user_accounts(db, user_id)