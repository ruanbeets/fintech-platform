from uuid import uuid4

from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.models.account import Account


def insert_transactions(df, account_id):

    db = SessionLocal()

    account = db.query(Account).filter(Account.account_id == account_id).first()

    if account is None:
        raise ValueError("Account not found")

    user_id = account.user_id

    rows = df.to_dict(orient="records")

    objects = []

    for row in rows:
        obj = Transaction(
            transaction_id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=row["date"],
            amount=row["amount"],
            description=row["description"],
            category=row.get("category")
        )

        objects.append(obj)

    db.bulk_save_objects(objects)

    db.commit()

    db.close()

    return len(objects)