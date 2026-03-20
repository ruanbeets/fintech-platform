from app.database.connection import SessionLocal
from app.models.transaction import Transaction


class TransactionsViewModel:

    @staticmethod
    def create_transaction(data: dict):
        db = SessionLocal()
        try:
            tx = Transaction(**data)
            db.add(tx)
            db.commit()
            db.refresh(tx)
            return tx
        finally:
            db.close()

    @staticmethod
    def get_transaction(transaction_id: str):
        db = SessionLocal()
        try:
            return db.query(Transaction)\
                     .filter(Transaction.id == transaction_id)\
                     .first()
        finally:
            db.close()

    @staticmethod
    def get_transactions(user_id: str):
        db = SessionLocal()
        try:
            return db.query(Transaction)\
                     .filter(Transaction.user_id == user_id)\
                     .order_by(Transaction.occurred_at.desc())\
                     .all()
        finally:
            db.close()

    @staticmethod
    def update_transaction(transaction_id: str, data: dict):
        db = SessionLocal()
        try:
            tx = db.query(Transaction)\
                   .filter(Transaction.id == transaction_id)\
                   .first()

            if not tx:
                return None

            for key, value in data.items():
                setattr(tx, key, value)

            db.commit()
            db.refresh(tx)
            return tx
        finally:
            db.close()

    @staticmethod
    def delete_transaction(transaction_id: str):
        db = SessionLocal()
        try:
            tx = db.query(Transaction)\
                   .filter(Transaction.id == transaction_id)\
                   .first()

            if not tx:
                return False

            db.delete(tx)
            db.commit()
            return True
        finally:
            db.close()