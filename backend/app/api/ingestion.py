from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/upload")
def ingest_file(
    user_id: UUID,
    account_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    return IngestionService.ingest_file(
        db=db,
        user_id=user_id,
        account_id=account_id,
        file=file.file
    )