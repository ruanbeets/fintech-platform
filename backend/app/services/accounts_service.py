from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.accounts_repository import (
    create_account,
    get_account_by_id,
    get_accounts_by_user,
    update_account_balance,
    delete_account
)


def create_new_account(db: Session, user_id: UUID, account_type: str, currency: str):
    return create_account(db, user_id, account_type, currency)


def fetch_account(db: Session, account_id: UUID):
    account = get_account_by_id(db, account_id)

    if not account:
        raise ValueError("Account not found")

    return account


def list_user_accounts(db: Session, user_id: UUID):
    return get_accounts_by_user(db, user_id)


def change_account_balance(db: Session, account_id: UUID, new_balance):
    return update_account_balance(db, account_id, new_balance)


def remove_account(db: Session, account_id: UUID):
    return delete_account(db, account_id)