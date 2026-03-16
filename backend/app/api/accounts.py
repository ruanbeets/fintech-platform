from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.accounts_service import AccountsService
from app.schemas.account_schema import AccountCreate

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/")
def create_account(user_id: UUID, account: AccountCreate, db: Session = Depends(get_db)):

    return AccountsService.create_account(
        db,
        user_id,
        account.name,
        account.institution
    )


@router.get("/user/{user_id}")
def get_user_accounts(user_id: UUID, db: Session = Depends(get_db)):

    return AccountsService.get_user_accounts(db, user_id)


@router.get("/{account_id}")
def get_account(account_id: UUID, db: Session = Depends(get_db)):

    try:

        return AccountsService.get_account(db, account_id)

    except ValueError as e:

        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{account_id}")
def delete_account(account_id: UUID, db: Session = Depends(get_db)):

    try:

        return AccountsService.delete_account(db, account_id)

    except ValueError as e:

        raise HTTPException(status_code=404, detail=str(e))