from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.viewmodels.transactions_vm import TransactionsViewModel
from app.viewmodels.accounts_vm import AccountsViewModel

router = APIRouter(prefix="/transactions")


@router.post("/")
def create_transaction(data: TransactionCreate):
    account = AccountsViewModel.get_account(data.account_id)
    if account is None or account.user_id != data.user_id:
        raise HTTPException(400, "Account must belong to the transaction user")
    return TransactionsViewModel.create_transaction(data.model_dump())


@router.get("/{user_id}")
def get_transactions(user_id: UUID):
    return TransactionsViewModel.get_transactions(user_id)


@router.get("/single/{transaction_id}")
def get_transaction(transaction_id: UUID):
    tx = TransactionsViewModel.get_transaction(transaction_id)
    if not tx:
        raise HTTPException(404, "transaction not found")
    return tx


@router.put("/{transaction_id}")
def update_transaction(transaction_id: UUID, data: TransactionUpdate):
    tx = TransactionsViewModel.update_transaction(transaction_id, data.model_dump(exclude_unset=True))
    if not tx:
        raise HTTPException(404, "transaction not found")
    return tx


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: UUID):
    success = TransactionsViewModel.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(404, "transaction not found")
    return {"message": "deleted"}
