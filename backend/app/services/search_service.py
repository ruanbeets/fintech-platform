from sqlalchemy.orm import Session
from uuid import UUID

from app.models.transaction import Transaction
from app.models.account import Account


class SearchService:

    @staticmethod
    def search_transactions(db: Session, user_id: UUID, query: str):

        return (
            db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.description.ilike(f"%{query}%")
            )
            .all()
        )


    @staticmethod
    def search_accounts(db: Session, user_id: UUID, query: str):

        return (
            db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.name.ilike(f"%{query}%")
            )
            .all()
        )


    @staticmethod
    def global_search(db: Session, user_id: UUID, query: str):

        transactions = SearchService.search_transactions(db, user_id, query)

        accounts = SearchService.search_accounts(db, user_id, query)

        return {
            "transactions": transactions,
            "accounts": accounts
        }