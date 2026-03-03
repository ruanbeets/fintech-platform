from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.deps import get_db
from backend.app.models.transaction import Transaction
from backend.app.models.schemas import TransactionCreate, TransactionResponse
import uuid

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()


@router.post("/", response_model=TransactionResponse)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    transaction = Transaction(**payload.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction