from sqlalchemy.orm import Session
from uuid import UUID

from app.models.account import Account


class AccountsRepository:

    @staticmethod
    def create(db: Session, user_id: UUID, name: str, institution: str | None):

        account = Account(
            user_id=user_id,
            name=name,
            institution=institution,
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        return account

    @staticmethod
    def get_by_id(db: Session, account_id: UUID):

        return db.query(Account).filter(Account.id == account_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: UUID):

        return db.query(Account).filter(Account.user_id == user_id).all()

    @staticmethod
    def delete(db: Session, account_id: UUID):

        account = db.query(Account).filter(Account.id == account_id).first()

        if account:
            db.delete(account)
            db.commit()

        return account