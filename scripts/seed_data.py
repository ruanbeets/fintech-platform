import uuid
from datetime import date

from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.transaction import Transaction


def seed():
    db = SessionLocal()

    # Create user
    user = User(
        email="test@example.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create account
    account = Account(
        user_id=user.user_id,
        account_type="broker",
        currency="USD"
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    # Create transaction
    transaction = Transaction(
        user_id=user.user_id,
        account_id=account.account_id,
        date=date.today(),
        amount=1000.00,
        category="Investment",
        description="Initial deposit"
    )
    db.add(transaction)
    db.commit()

    db.close()

    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()