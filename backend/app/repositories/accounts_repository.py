from sqlalchemy.orm import Session
from uuid import UUID

from app.models.account import Account


def create_account(db: Session, user_id: UUID, account_type: str, currency: str) -> Account:
    account = Account(
        user_id=user_id,
        account_type=account_type,
        currency=currency
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


def get_account_by_id(db: Session, account_id: UUID) -> Account | None:
    return db.query(Account).filter(Account.account_id == account_id).first()


def get_accounts_by_user(db: Session, user_id: UUID):
    return db.query(Account).filter(Account.user_id == user_id).all()


def update_account_balance(db: Session, account_id: UUID, new_balance):
    account = db.query(Account).filter(Account.account_id == account_id).first()

    if account:
        account.balance = new_balance
        db.commit()
        db.refresh(account)

    return account


def delete_account(db: Session, account_id: UUID):
    account = db.query(Account).filter(Account.account_id == account_id).first()

    if account:
        db.delete(account)
        db.commit()

    return account