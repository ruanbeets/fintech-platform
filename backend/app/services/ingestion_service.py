from sqlalchemy.orm import Session

from app.ingestion.parser import parse_file
from app.ingestion.cleaner import clean_transactions
from app.ingestion.validator import validate_transactions

from app.repositories.transactions_repository import TransactionsRepository


class IngestionService:

    @staticmethod
    def ingest_file(db: Session, user_id, account_id, file):

        raw_transactions = parse_file(file)

        cleaned = clean_transactions(raw_transactions)

        validated = validate_transactions(cleaned)

        created = []

        for t in validated:

            transaction = TransactionsRepository.create(
                db=db,
                user_id=user_id,
                account_id=account_id,
                amount=t["amount"],
                description=t.get("description"),
                category_id=t.get("category_id"),
                type=t["type"]
            )

            created.append(transaction)

        return created