from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.deps import get_db
from backend.app.models.transaction import Transaction
from backend.app.models.schemas import TransactionCreate, TransactionResponse
from backend.app.models.account import Account
from sqlalchemy import func
import uuid

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

@router.get("/summary")
def get_summary(user_id: uuid.UUID, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).all()

    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(t.amount for t in transactions if t.amount < 0)
    net_cashflow = total_income + total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cashflow": net_cashflow
    }

@router.get("/category-summary")
def category_summary(user_id: uuid.UUID, db: Session = Depends(get_db)):
    results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        )
        .filter(Transaction.user_id == user_id)
        .group_by(Transaction.category)
        .all()
    )

    return {
        category: float(total)
        for category, total in results
    }

@router.post("/", response_model=TransactionResponse)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):

    # Create transaction object
    transaction = Transaction(**payload.model_dump())

    # Find related account
    account = db.query(Account).filter(
        Account.account_id == payload.account_id
    ).first()

    # Update account balance
    account.balance += float(payload.amount)

    # Save transaction
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        return {"error": "Transaction not found"}

    # Reverse balance effect
    account = db.query(Account).filter(
        Account.account_id == transaction.account_id
    ).first()

    account.balance -= float(transaction.amount)

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted"}