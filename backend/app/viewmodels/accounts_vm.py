from app.database.connection import SessionLocal
from app.models.account import Account


class AccountsViewModel:

    @staticmethod
    def create_account(data: dict):
        db = SessionLocal()
        try:
            account = Account(**data)
            db.add(account)
            db.commit()
            db.refresh(account)
            return account
        finally:
            db.close()

    @staticmethod
    def get_account(account_id: str):
        db = SessionLocal()
        try:
            return db.query(Account).filter(Account.id == account_id).first()
        finally:
            db.close()

    @staticmethod
    def get_accounts(user_id: str):
        db = SessionLocal()
        try:
            return db.query(Account)\
                     .filter(Account.user_id == user_id)\
                     .all()
        finally:
            db.close()

    @staticmethod
    def update_account(account_id: str, data: dict):
        db = SessionLocal()
        try:
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return None

            for key, value in data.items():
                setattr(account, key, value)

            db.commit()
            db.refresh(account)
            return account
        finally:
            db.close()

    @staticmethod
    def delete_account(account_id: str):
        db = SessionLocal()
        try:
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return False

            db.delete(account)
            db.commit()
            return True
        finally:
            db.close()