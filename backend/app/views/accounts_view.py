from fastapi import APIRouter, HTTPException
from app.viewmodels.accounts_vm import AccountsViewModel

router = APIRouter(prefix="/accounts")


VALID_TYPES = ["bank", "card", "cash", "crypto", "investment"]


@router.post("/")
def create_account(data: dict):
    required = ["user_id", "name", "type", "currency"]

    for f in required:
        if f not in data:
            raise HTTPException(400, f"{f} required")

    if data["type"] not in VALID_TYPES:
        raise HTTPException(400, "invalid account type")

    if len(data["currency"]) != 3:
        raise HTTPException(400, "currency must be 3-letter code")

    return AccountsViewModel.create_account(data)


@router.get("/{user_id}")
def get_accounts(user_id: str):
    return AccountsViewModel.get_accounts(user_id)


@router.get("/single/{account_id}")
def get_account(account_id: str):
    acc = AccountsViewModel.get_account(account_id)
    if not acc:
        raise HTTPException(404, "account not found")
    return acc


@router.put("/{account_id}")
def update_account(account_id: str, data: dict):
    if "type" in data and data["type"] not in VALID_TYPES:
        raise HTTPException(400, "invalid account type")

    if "currency" in data and len(data["currency"]) != 3:
        raise HTTPException(400, "currency must be 3-letter code")

    acc = AccountsViewModel.update_account(account_id, data)
    if not acc:
        raise HTTPException(404, "account not found")

    return acc


@router.delete("/{account_id}")
def delete_account(account_id: str):
    success = AccountsViewModel.delete_account(account_id)
    if not success:
        raise HTTPException(404, "account not found")

    return {"message": "deleted"}