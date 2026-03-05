from app.db.session import SessionLocal
from app.models.transaction import Transaction


def insert_transactions(df):

    db = SessionLocal()

    rows = df.to_dict(orient="records")

    objects = []

    for row in rows:
        obj = Transaction(
            date=row["date"],
            amount=row["amount"],
            description=row["description"],
        )
        objects.append(obj)

    db.bulk_save_objects(objects)

    db.commit()

    db.close()

    return len(objects)