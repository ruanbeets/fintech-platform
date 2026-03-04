from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.deps import get_db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.schemas import AccountCreate, AccountResponse
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

    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    results = []

    for account in accounts:
        balance = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(Transaction.account_id == account.account_id)
            .scalar()
        )

        account_dict = account.__dict__.copy()
        account_dict["balance"] = float(balance)

        results.append(account_dict)

    return results