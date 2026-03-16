from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.transactions_service import TransactionsService
from app.schemas.transaction_schema import TransactionCreate

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/")
def create_transaction(
    user_id: UUID,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):

    return TransactionsService.create_transaction(
        db=db,
        user_id=user_id,
        account_id=transaction.account_id,
        amount=transaction.amount,
        description=transaction.description,
        category_id=transaction.category_id,
        type=transaction.type,
    )


@router.get("/user/{user_id}")
def get_user_transactions(user_id: UUID, db: Session = Depends(get_db)):

    return TransactionsService.get_user_transactions(db, user_id)


@router.get("/account/{account_id}")
def get_account_transactions(account_id: UUID, db: Session = Depends(get_db)):

    return TransactionsService.get_account_transactions(db, account_id)


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: UUID, db: Session = Depends(get_db)):

    try:

        return TransactionsService.delete_transaction(db, transaction_id)

    except ValueError as e:

        raise HTTPException(status_code=404, detail=str(e))