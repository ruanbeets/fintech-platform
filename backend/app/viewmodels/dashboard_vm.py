from datetime import datetime, timezone
from app.database.connection import SessionLocal
from app.models.account import Account
from app.models.transaction import Transaction
from app.services.financial_analytics import calculate_overview


class DashboardViewModel:
    @staticmethod
    def get_summary(user_id, *, month=None, currency=None, demo=False, as_of=None):
        with SessionLocal() as db:
            accounts = db.query(Account).filter(Account.user_id == user_id).order_by(Account.name).all()
            transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
            return calculate_overview(accounts, transactions, user_id=user_id,
                                      as_of=as_of or datetime.now(timezone.utc).date(),
                                      selected_month=month, currency=currency, demo=demo)
