from sqlalchemy.orm import Session
from uuid import UUID

from app.models.transaction import Transaction


class TransactionsRepository:

    @staticmethod
    def create(
        db: Session,
        user_id: UUID,
        account_id: UUID,
        amount: float,
        description: str | None,
        category_id: UUID | None,
        type: str,
    ):

        transaction = Transaction(
            user_id=user_id,
            account_id=account_id,
            amount=amount,
            description=description,
            category_id=category_id,
            type=type,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    @staticmethod
    def get_by_id(db: Session, transaction_id: UUID):

        return (
            db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

    @staticmethod
    def get_by_user(db: Session, user_id: UUID):

        return (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .all()
        )

    @staticmethod
    def get_by_account(db: Session, account_id: UUID):

        return (
            db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .all()
        )

    @staticmethod
    def delete(db: Session, transaction_id: UUID):

        transaction = (
            db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

        if transaction:
            db.delete(transaction)
            db.commit()

        return transaction