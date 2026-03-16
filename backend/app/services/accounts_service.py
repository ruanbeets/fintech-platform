from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.accounts_repository import AccountsRepository
from app.repositories.transactions_repository import TransactionsRepository


class AccountsService:

    @staticmethod
    def create_account(db: Session, user_id: UUID, name: str, institution: str | None):

        return AccountsRepository.create(
            db=db,
            user_id=user_id,
            name=name,
            institution=institution,
        )


    @staticmethod
    def get_account(db: Session, account_id: UUID):

        account = AccountsRepository.get_by_id(db, account_id)

        if not account:
            raise ValueError("Account not found")

        return account


    @staticmethod
    def get_user_accounts(db: Session, user_id: UUID):

        return AccountsRepository.get_by_user(db, user_id)


    @staticmethod
    def delete_account(db: Session, account_id: UUID):

        account = AccountsRepository.delete(db, account_id)

        if not account:
            raise ValueError("Account not found")

        return account


    @staticmethod
    def calculate_account_balance(db: Session, account_id: UUID):

        transactions = TransactionsRepository.get_by_account(db, account_id)

        balance = 0

        for t in transactions:

            if t.type == "income":
                balance += t.amount
            else:
                balance -= t.amount

        return balance