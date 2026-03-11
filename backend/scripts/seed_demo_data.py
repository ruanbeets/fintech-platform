import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
import uuid
from datetime import date, timedelta

from app.database.session import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.database.base import Base
from app.database.session import engine


CATEGORIES = [
    "Food",
    "Transport",
    "Salary",
    "Shopping",
    "Entertainment",
    "Utilities",
    "Investment",
    "Transfer"
]


def create_transactions(db, user_id, account_id, start_balance=10000):

    balance = start_balance
    start_date = date(2025, 1, 1)

    transactions = []

    for i in range(60):

        tx_date = start_date + timedelta(days=i * 2)

        category = random.choice(CATEGORIES)

        if category == "Salary":
            amount = random.randint(2000, 4000)
        else:
            amount = random.randint(-300, -20)

        balance += amount

        tx = Transaction(
            transaction_id=uuid.uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=tx_date,
            amount=amount,
            balance=balance,
            category=category,
            description=f"{category} transaction"
        )

        transactions.append(tx)

    db.add_all(transactions)


def seed():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    print("Seeding demo data...")

    # -------- USERS --------

    users = [
        User(email="student@demo.com"),
        User(email="professional@demo.com"),
        User(email="investor@demo.com")
    ]

    db.add_all(users)
    db.commit()

    for user in users:
        db.refresh(user)

    # -------- ACCOUNTS --------

    accounts = []

    for user in users:

        acc = Account(
            account_id=uuid.uuid4(),
            user_id=user.user_id,
            account_type="bank",
            currency="ZAR",
            balance=10000
        )

        accounts.append(acc)

    db.add_all(accounts)
    db.commit()

    for acc in accounts:
        db.refresh(acc)

    # -------- TRANSACTIONS --------

    for acc in accounts:

        create_transactions(
            db,
            acc.user_id,
            acc.account_id
        )

    db.commit()
    db.close()

    print("Demo data seeded successfully.")


if __name__ == "__main__":
    seed()