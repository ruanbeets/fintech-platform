from fastapi import APIRouter, UploadFile, File

from app.ingestion.parser import parse_file
from app.ingestion.cleaner import clean_transactions
from app.ingestion.validator import validate_transactions
from app.ingestion.service import insert_transactions


router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/transactions")
async def upload_transactions(file: UploadFile = File(...)):

    contents = await file.read()

    df = parse_file(file.filename, contents)

    df = clean_transactions(df)

    validate_transactions(df)

    inserted = insert_transactions(df)

    return {"rows_inserted": inserted}