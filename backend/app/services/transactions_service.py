from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.transactions_repository import TransactionsRepository
from app.domain.categorization.classifier import classify_transaction
from app.domain.events.transaction_created import handle_transaction_created
from app.domain.events.large_transaction import detect_large_transaction


class TransactionsService:

    @staticmethod
    def create_transaction(
        db: Session,
        user_id: UUID,
        account_id: UUID,
        amount: float,
        description: str | None,
        category_id,
        type: str,
    ):

        if not category_id and description:
            category_name = classify_transaction(
                type("obj", (), {"description": description})
            )

        transaction = TransactionsRepository.create(
            db=db,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
            description=description,
            category_id=category_id,
            type=type,
        )

        events = []

        created_events = handle_transaction_created(transaction)

        if created_events:
            events.extend(created_events)

        large_event = detect_large_transaction(transaction)

        if large_event:
            events.append(large_event)

        return {
            "transaction": transaction,
            "events": events
        }


    @staticmethod
    def get_user_transactions(db: Session, user_id: UUID):

        return TransactionsRepository.get_by_user(db, user_id)


    @staticmethod
    def get_account_transactions(db: Session, account_id: UUID):

        return TransactionsRepository.get_by_account(db, account_id)


    @staticmethod
    def delete_transaction(db: Session, transaction_id: UUID):

        transaction = TransactionsRepository.delete(db, transaction_id)

        if not transaction:
            raise ValueError("Transaction not found")

        return transaction