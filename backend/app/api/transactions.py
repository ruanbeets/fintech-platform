from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.schemas.transaction_schema import (
    TransactionCreate,
    TransactionResponse
)

from app.services.transactions_service import (
    create_new_transaction,
    list_user_transactions,
    fetch_transaction,
    remove_transaction
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(user_id: UUID, db: Session = Depends(get_db)):
    return list_user_transactions(db, user_id)


@router.post("/", response_model=TransactionResponse)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    return create_new_transaction(
        db,
        payload.user_id,
        payload.account_id,
        payload.date,
        payload.amount,
        payload.amount,
        payload.category,
        payload.description
    )


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: UUID, db: Session = Depends(get_db)):
    return remove_transaction(db, transaction_id)