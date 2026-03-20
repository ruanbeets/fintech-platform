from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.viewmodels.transactions_vm import TransactionsViewModel

router = APIRouter(prefix="/transactions")

VALID_TYPES = ["income", "expense", "transfer"]


@router.post("/")
def create_transaction(data: dict):
    required = ["user_id", "account_id", "amount", "type", "occurred_at"]

    for f in required:
        if f not in data:
            raise HTTPException(400, f"{f} required")

    if data["type"] not in VALID_TYPES:
        raise HTTPException(400, "invalid type")

    try:
        data["amount"] = float(data["amount"])
    except:
        raise HTTPException(400, "amount must be numeric")

    if data["amount"] <= 0:
        raise HTTPException(400, "amount must be > 0")

    try:
        data["occurred_at"] = datetime.fromisoformat(data["occurred_at"])
    except:
        raise HTTPException(400, "invalid datetime format")

    return TransactionsViewModel.create_transaction(data)


@router.get("/{user_id}")
def get_transactions(user_id: str):
    return TransactionsViewModel.get_transactions(user_id)


@router.get("/single/{transaction_id}")
def get_transaction(transaction_id: str):
    tx = TransactionsViewModel.get_transaction(transaction_id)
    if not tx:
        raise HTTPException(404, "transaction not found")
    return tx


@router.put("/{transaction_id}")
def update_transaction(transaction_id: str, data: dict):

    if "type" in data and data["type"] not in VALID_TYPES:
        raise HTTPException(400, "invalid type")

    if "amount" in data:
        try:
            data["amount"] = float(data["amount"])
        except:
            raise HTTPException(400, "amount must be numeric")

    if "occurred_at" in data:
        try:
            data["occurred_at"] = datetime.fromisoformat(data["occurred_at"])
        except:
            raise HTTPException(400, "invalid datetime")

    tx = TransactionsViewModel.update_transaction(transaction_id, data)
    if not tx:
        raise HTTPException(404, "transaction not found")

    return tx


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: str):
    success = TransactionsViewModel.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(404, "transaction not found")

    return {"message": "deleted"}