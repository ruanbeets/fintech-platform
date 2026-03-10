from fastapi import APIRouter, UploadFile, File, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.ingestion.parser import parse_file
from app.ingestion.cleaner import clean_transactions
from app.ingestion.validator import validate_transactions

from app.services.ingestion_service import insert_transactions

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/transactions")
async def upload_transactions(
    account_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    contents = await file.read()

    df = parse_file(file.filename, contents)

    df = clean_transactions(df)

    validate_transactions(df)

    inserted = insert_transactions(db, df, account_id)

    return {"rows_inserted": inserted}