from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.account import Account


def insert_transactions(db: Session, df, account_id):

    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if account is None:
        raise ValueError("Account not found")

    user_id = account.user_id

    rows = df.to_dict(orient="records")

    rows.sort(key=lambda r: r["date"])

    inserted = 0

    for row in rows:

        tx = Transaction(
            transaction_id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=row["date"],
            amount=row["amount"],
            balance=row["balance"],
            description=row["description"],
            category=row.get("category")
        )

        db.add(tx)

        inserted += 1

    account.balance = rows[-1]["balance"]

    db.commit()

    return inserted