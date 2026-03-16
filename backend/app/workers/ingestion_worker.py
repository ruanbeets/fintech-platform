from app.database.session import SessionLocal
from app.services.ingestion_service import IngestionService
from app.core.logging import get_logger

logger = get_logger(__name__)


class IngestionWorker:

    @staticmethod
    def process_file(user_id, account_id, file_path):

        db = SessionLocal()

        try:

            logger.info(f"Processing ingestion file {file_path}")

            with open(file_path, "rb") as f:

                transactions = IngestionService.ingest_file(
                    db=db,
                    user_id=user_id,
                    account_id=account_id,
                    file=f
                )

            logger.info(f"Ingested {len(transactions)} transactions")

            return transactions

        except Exception as e:

            logger.error(f"Ingestion failed: {e}")
            raise

        finally:

            db.close()