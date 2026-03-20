from app.database.connection import SessionLocal
from app.models.transaction import Transaction
from sqlalchemy import func


class DashboardViewModel:

    @staticmethod
    def get_summary(user_id: str):
        db = SessionLocal()
        try:
            income = db.query(func.coalesce(func.sum(Transaction.amount), 0))\
                .filter(Transaction.user_id == user_id)\
                .filter(Transaction.type == "income")\
                .scalar()

            expense = db.query(func.coalesce(func.sum(Transaction.amount), 0))\
                .filter(Transaction.user_id == user_id)\
                .filter(Transaction.type == "expense")\
                .scalar()

            return {
                "income": float(income),
                "expense": float(expense),
                "net": float(income - expense),
            }
        finally:
            db.close()