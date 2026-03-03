from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.deps import get_db
from backend.app.models.account import Account
from backend.app.models.schemas import AccountCreate, AccountResponse
import uuid

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    account = Account(**payload.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/", response_model=list[AccountResponse])
def get_accounts(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Account).filter(Account.user_id == user_id).all()