from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.deps import get_db
from backend.app.models.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions