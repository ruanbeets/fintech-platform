from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.transactions_repository import (
    create_transaction,
    get_transaction_by_id,
    get_transactions_by_account,
    get_transactions_by_user,
    delete_transaction
)


def create_new_transaction(
    db: Session,
    user_id: UUID,
    account_id: UUID,
    date,
    amount,
    balance,
    category=None,
    description=None
):
    return create_transaction(
        db,
        user_id,
        account_id,
        date,
        amount,
        balance,
        category,
        description
    )


def fetch_transaction(db: Session, transaction_id: UUID):
    tx = get_transaction_by_id(db, transaction_id)

    if not tx:
        raise ValueError("Transaction not found")

    return tx


def list_account_transactions(db: Session, account_id: UUID):
    return get_transactions_by_account(db, account_id)


def list_user_transactions(db: Session, user_id: UUID):
    return get_transactions_by_user(db, user_id)


def remove_transaction(db: Session, transaction_id: UUID):
    return delete_transaction(db, transaction_id)