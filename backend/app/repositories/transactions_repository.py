from sqlalchemy.orm import Session
from uuid import UUID

from app.models.transaction import Transaction


def create_transaction(
    db: Session,
    user_id: UUID,
    account_id: UUID,
    date,
    amount,
    balance,
    category=None,
    description=None
) -> Transaction:

    transaction = Transaction(
        user_id=user_id,
        account_id=account_id,
        date=date,
        amount=amount,
        balance=balance,
        category=category,
        description=description
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def get_transaction_by_id(db: Session, transaction_id: UUID):
    return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()


def get_transactions_by_account(db: Session, account_id: UUID):
    return db.query(Transaction).filter(Transaction.account_id == account_id).all()


def get_transactions_by_user(db: Session, user_id: UUID):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()


def delete_transaction(db: Session, transaction_id: UUID):
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if transaction:
        db.delete(transaction)
        db.commit()

    return transaction