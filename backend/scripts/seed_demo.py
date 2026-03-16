import sys
import os
import uuid
from datetime import date, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import SessionLocal, engine
from app.database.base import Base

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


START_DATE = date(2025, 1, 1)
DAYS = 180  # 6 months of transactions


def create_transactions(db, user_id, account_id, start_balance=20000):

    balance = start_balance
    transactions = []

    for day in range(DAYS):

        tx_date = START_DATE + timedelta(days=day)
        weekday = tx_date.weekday()

        amount = None
        category = None
        description = None

        # ---------------- SALARY ----------------
        if tx_date.day == 1:
            amount = 35000
            category = "Salary"
            description = "Monthly Salary"

        # ---------------- RENT ----------------
        elif tx_date.day == 3:
            amount = -12000
            category = "Utilities"
            description = "Rent Payment"

        # ---------------- WEEKLY GROCERIES ----------------
        elif weekday == 5:
            amount = -850
            category = "Food"
            description = "Weekly Groceries"

        # ---------------- DAILY COMMUTE ----------------
        elif weekday < 5:
            amount = -120
            category = "Transport"
            description = "Work Commute"

        # ---------------- INVESTMENTS (UPWARD TREND) ----------------
        elif day % 30 == 10:
            amount = -(1000 + day * 5)
            category = "Investment"
            description = "Investment Contribution"

        # ---------------- WEEKEND ENTERTAINMENT ----------------
        elif weekday == 6:
            amount = -400
            category = "Entertainment"
            description = "Weekend Activity"

        # ---------------- OCCASIONAL SHOPPING SPIKES ----------------
        elif day in [45, 90, 135]:
            amount = -5000
            category = "Shopping"
            description = "Large Purchase"

        else:
            continue

        balance += amount

        tx = Transaction(
            transaction_id=uuid.uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=tx_date,
            amount=amount,
            balance=balance,
            category=category,
            description=description,
        )

        transactions.append(tx)

    db.add_all(transactions)


def seed():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    print("Seeding demo data...")

    # ---------------- CLEAN EXISTING DATA ----------------
    db.query(Transaction).delete()
    db.query(Account).delete()
    db.query(User).delete()
    db.commit()

    # ---------------- CREATE USER ----------------
    user = User(
        email="demo@fintrack.com",
        hashed_password="demo123",
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # ---------------- CREATE ACCOUNTS ----------------
    account_types = [
        "Daily Spending",
        "Savings",
        "Investment"
    ]

    accounts = []

    for acc_type in account_types:

        acc = Account(
            id=uuid.uuid4(),
            user_id=user.id,
            account_type=acc_type,
            currency="ZAR",
            balance=20000
        )

        accounts.append(acc)

    db.add_all(accounts)
    db.commit()

    for acc in accounts:
        db.refresh(acc)

    # ---------------- CREATE TRANSACTIONS ----------------
    for acc in accounts:

        create_transactions(
            db,
            user.id,
            acc.id,
            start_balance=20000
        )

    db.commit()
    db.close()

    print("Demo data seeded successfully.")


if __name__ == "__main__":
    seed()