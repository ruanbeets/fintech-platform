"""Reproducible synthetic ZAR fixture. Inserts missing fixture rows; never deletes."""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid5
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.services.financial_analytics import shift_month

NAMESPACE = UUID("d5feb123-1996-492a-99ad-6c2350ba3a91")
DEMO_USER_ID = uuid5(NAMESPACE, "demo-user-v1")
DEMO_EMAIL = "overview-demo@fintrack.invalid"
START_MONTH = date(2024, 9, 1)
MONTHS = 24


def fixture_id(key):
    return uuid5(NAMESPACE, key)


def transaction_rows():
    for index in range(MONTHS):
        month = shift_month(START_MONTH, index)
        # Deliberate gap: no import for November 2025, not verified zero spending.
        if month == date(2025, 11, 1):
            continue
        rows = [
            ("salary", 25, Decimal("38500") if index < 12 else Decimal("42000"), "income", "Salary", "Cape Software Studio"),
            ("rent", 1, Decimal("11200") if index < 12 else Decimal("11850"), "expense", "Housing", "Monthly rent"),
            ("utilities", 3, Decimal(1350 + index % 4 * 95), "expense", "Utilities", "Electricity and water"),
            ("insurance", 4, Decimal("890.50"), "expense", "Insurance", "Vehicle insurance"),
            ("internet", 5, Decimal("749"), "expense", "Connectivity", "Fibre connection"),
            ("transport", 8, Decimal(1550 + index % 3 * 180), "expense", "Transport", "Fuel and commuting"),
            ("dining", 19, Decimal(980 + index % 5 * 155), "expense", "Dining", "Restaurants and coffee"),
            ("health", 21, Decimal(350 + index % 4 * 120), "expense", "Health", "Pharmacy and care"),
            ("savings", 26, Decimal("4500"), "transfer", "Savings", "Savings contribution"),
        ]
        for week, day in enumerate([6, 13, 20, 27]):
            rows.append((f"groceries-{week}", day, Decimal(780 + (index + week) % 5 * 63) + Decimal("0.45"),
                         "expense", "Groceries", "Weekly groceries"))
        if month.month == 12:
            rows += [("bonus", 15, Decimal("12000"), "income", "Bonus", "Annual bonus"),
                     ("travel", 18, Decimal("8200"), "expense", "Travel", "Summer holiday")]
        if index % 4 == 2:
            rows.append(("freelance", 16, Decimal("2750"), "income", "Freelance", "Design project"))
        if index % 6 == 4:
            rows.append(("maintenance", 12, Decimal("3200"), "expense", "Maintenance", "Car service"))
        for key, day, amount, kind, category, description in rows:
            yield dict(id=fixture_id(f"{month.isoformat()}-{key}"), user_id=DEMO_USER_ID,
                       account_id=fixture_id("everyday-account"), amount=amount, type=kind,
                       category=category, merchant=description, description=f"Synthetic demo: {description}",
                       occurred_at=datetime(month.year, month.month, day, 12))


def seed_demo(db):
    user = db.get(User, DEMO_USER_ID)
    if user is None:
        if db.query(User).filter(User.email == DEMO_EMAIL).first():
            raise ValueError("Demo email is already used by a different user; no records changed")
        db.add(User(id=DEMO_USER_ID, email=DEMO_EMAIL, password_hash="!local-demo-login-disabled!"))
        db.flush()
    elif user.email != DEMO_EMAIL:
        raise ValueError("Demo user ID collision; no records changed")
    for key, name in [("everyday-account", "Everyday account"), ("savings-account", "Savings account")]:
        account_id = fixture_id(key)
        account = db.get(Account, account_id)
        if account is None:
            db.add(Account(id=account_id, user_id=DEMO_USER_ID, name=name, type="bank", currency="ZAR"))
        elif account.user_id != DEMO_USER_ID or account.currency != "ZAR":
            raise ValueError("Demo account collision; no records changed")
    db.flush()
    added = 0
    for row in transaction_rows():
        existing = db.get(Transaction, row["id"])
        if existing is None:
            db.add(Transaction(**row))
            added += 1
        elif existing.user_id != DEMO_USER_ID or existing.account_id != row["account_id"]:
            raise ValueError("Demo transaction collision; no records changed")
    db.flush()
    return added


if __name__ == "__main__":
    from app.database.connection import SessionLocal
    from app.database.init_db import init_db
    init_db()
    with SessionLocal.begin() as session:
        count = seed_demo(session)
    print(f"Demo ready: {count} transactions added; unrelated records preserved.")
