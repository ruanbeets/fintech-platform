"""Reviewed imports; ownership always comes from a secret session capability."""
import asyncio
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4
from urllib.parse import unquote
from fastapi import APIRouter, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool
from app.database.connection import SessionLocal
from app.models.imports import ImportBatch, ImportedTransaction
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.imports import ReviewRequest, ReviewResponse, ConfirmRequest, ConfirmResponse
from app.schemas.imports import DetectionResponse, SessionResponse
from app.schemas.dashboard import DashboardSummary
from app.services.file_parser import parse_bounded, detect_header, detect_mapping, MAX_BYTES
from app.services.import_normalization import normalize_rows, fingerprint, amount_model, apply_duplicates
from app.services.import_reconciliation import reconcile
from app.services.import_detection import suggestions
from app.services.import_sessions import create_session, require_session, delete_session, cleanup_expired
from app.viewmodels.dashboard_vm import DashboardViewModel

router = APIRouter(prefix="/imports", tags=["Reviewed imports"])
parser_slots = asyncio.Semaphore(2)


class DetectRequest(BaseModel):
    sheet: str = Field(max_length=200)
    header_row: int | None = Field(default=None, ge=1, le=50)


def owned_batch(db, session, batch_id, pending=True):
    batch = db.query(ImportBatch).filter_by(id=batch_id, session_id=session.id).with_for_update().first()
    if batch is None:
        raise HTTPException(404, "Import not found.")
    if pending and (batch.status != "pending" or batch.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None)):
        raise HTTPException(409, "Preview expired or already imported. Upload again.")
    return batch


def detection(batch, sheet, header=None):
    rows = (batch.tables or {}).get(sheet)
    if not rows:
        raise HTTPException(422, "Choose a non-empty sheet.")
    header = header or detect_header(rows)
    if header > len(rows):
        raise HTTPException(422, "Header row is outside this sheet.")
    headers = rows[header - 1]
    mapping = detect_mapping(headers)
    defaults, high = suggestions(rows, header, mapping)
    # Keep source identifiers as strings internally, but omit them from previews.
    sensitive = mapping["account"]["candidates"] + mapping["source_reference"]["candidates"]
    preview = [["[account/reference hidden]" if i in sensitive else value for i, value in enumerate(row)] for row in rows[header:header+10]]
    return {"batch_id": str(batch.id), "file_type": batch.file_type, "sheets": list(batch.tables),
            "sheet": sheet, "header_row": header, "headers": headers, "mapping": mapping,
            "preview": preview, "row_count": len(rows) - header, "defaults": defaults, "high_confidence": high}


@router.post("/session", status_code=201, response_model=SessionResponse)
def start_session():
    with SessionLocal.begin() as db:
        cleanup_expired(db)
        return create_session(db)


@router.delete("/session", status_code=204)
def erase_session(x_demo_session: str | None = Header(default=None)):
    with SessionLocal.begin() as db:
        delete_session(db, require_session(db, x_demo_session, lock=True))


@router.post("/upload", response_model=DetectionResponse)
async def upload(request: Request, x_file_name: str = Header(default="upload.csv"),
                 x_demo_session: str | None = Header(default=None)):
    # Check ownership/quota before consuming a potentially expensive file.
    with SessionLocal() as db:
        session = require_session(db, x_demo_session)
        if db.query(ImportBatch).filter_by(session_id=session.id).count() >= 20:
            raise HTTPException(429, "Demo limit: 20 uploads per session. Delete this session to start over.")
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > MAX_BYTES:
            raise HTTPException(413, "Upload limit: 5 MB.")
    filename = unquote(x_file_name).replace("\\", "/").split("/")[-1][:160]
    if not filename or any(ord(c) < 32 for c in filename):
        raise HTTPException(422, "Invalid file name.")
    try:
        async with parser_slots:
            kind, tables = await run_in_threadpool(parse_bounded, bytes(content), filename)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    finally:
        content.clear()
    with SessionLocal.begin() as db:
        session = require_session(db, x_demo_session, lock=True)
        if db.query(ImportBatch).filter_by(session_id=session.id).count() >= 20:
            raise HTTPException(429, "Demo upload limit reached.")
        batch = ImportBatch(id=uuid4(), session_id=session.id, source_file=filename, file_type=kind,
                            tables=tables, expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1))
        db.add(batch)
        sheet = max(tables, key=lambda name: sum(v["confidence"] == "high" for v in
                    detect_mapping(tables[name][detect_header(tables[name])-1] if tables[name] else []).values()))
        return detection(batch, sheet)


@router.post("/{batch_id}/detect", response_model=DetectionResponse)
def detect(batch_id: UUID, options: DetectRequest, x_demo_session: str | None = Header(default=None)):
    with SessionLocal.begin() as db:
        batch = owned_batch(db, require_session(db, x_demo_session), batch_id)
        return detection(batch, options.sheet, options.header_row)


@router.post("/{batch_id}/review", response_model=ReviewResponse)
def review(batch_id: UUID, options: ReviewRequest, x_demo_session: str | None = Header(default=None)):
    with SessionLocal.begin() as db:
        session = require_session(db, x_demo_session, lock=True)
        batch = owned_batch(db, session, batch_id)
        rows = batch.tables.get(options.sheet)
        if not rows or options.header_row > len(rows):
            raise HTTPException(422, "Select a valid sheet and header row.")
        existing = {r[0] for r in db.query(ImportedTransaction.fingerprint).filter_by(session_id=session.id)}
        try:
            normalized = normalize_rows(rows, options, batch.id, batch.source_file, existing, check_duplicates=False)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        reconciliation = reconcile(normalized)
        apply_duplicates(normalized, existing)
        counts = {status: sum(r.status == status for r in normalized) for status in ["valid", "invalid", "duplicate", "excluded"]}
        income = sum((r.transaction.amount for r in normalized if r.status == "valid" and r.transaction.transaction_type == "income"), Decimal("0.00"))
        expenses = sum((r.transaction.amount for r in normalized if r.status == "valid" and r.transaction.transaction_type == "expense"), Decimal("0.00"))
        response = ReviewResponse(batch_id=batch.id, review_id=secrets.token_hex(24), detected=len(normalized),
                                  valid=counts["valid"] + counts["duplicate"], invalid=counts["invalid"],
                                  duplicates=counts["duplicate"], excluded=counts["excluded"], to_import=counts["valid"],
                                  income=income, expenses=expenses, net_cash_flow=income-expenses,
                                  currency=options.currency, rows=normalized,
                                  warning="Verify classifications, especially transfers. Totals cover new rows. Repeated no-balance payments are retained; matches across uploads are possible duplicates and skipped. Balances verify statement movements, not account valuations.",
                                  reconciliation=reconciliation,
                                  amount_model={"signed": "SIGNED AMOUNT", "debit_credit": "DEBIT/CREDIT", "money_columns": "MONEY IN/MONEY OUT"}[amount_model(rows[options.header_row-1], options.mapping, options.amount_model, rows[options.header_row:])] + ("/FEE" if options.mapping.fee is not None else ""),
                                  account_count=len({r.transaction.account for r in normalized if r.transaction}),
                                  date_start=min((r.transaction.date.date().isoformat() for r in normalized if r.transaction), default=None),
                                  date_end=max((r.transaction.date.date().isoformat() for r in normalized if r.transaction), default=None))
        batch.review = response.model_dump(mode="json")
        batch.review_id = response.review_id
        return response


@router.post("/{batch_id}/confirm", response_model=ConfirmResponse)
def confirm(batch_id: UUID, options: ConfirmRequest, x_demo_session: str | None = Header(default=None)):
    try:
        with SessionLocal.begin() as db:
            session = require_session(db, x_demo_session, lock=True)
            batch = owned_batch(db, session, batch_id, pending=False)
            if batch.status == "committed" and batch.review_id == options.review_id:
                return batch.result
            if batch.status != "pending" or batch.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None) or batch.review_id != options.review_id or not batch.review:
                raise HTTPException(409, "Review has changed or expired. Validate again.")
            reviewed = ReviewResponse.model_validate(batch.review)
            if reviewed.invalid and not options.skip_invalid:
                raise HTTPException(422, "Resolve invalid rows or explicitly choose to skip them.")
            if db.query(Transaction).filter_by(user_id=session.user_id).count() + reviewed.to_import > 20000:
                raise HTTPException(429, "Demo limit: 20,000 imported transactions per session.")
            existing = {r[0] for r in db.query(ImportedTransaction.fingerprint).filter_by(session_id=session.id)}
            imported, duplicates = 0, reviewed.duplicates
            committed_rows = []
            for item in reviewed.rows:
                if item.status != "valid":
                    continue
                row = item.transaction
                key = fingerprint(row)
                if key in existing:
                    duplicates += 1
                    continue
                account = db.query(Account).filter_by(user_id=session.user_id, name=row.account.casefold(), currency=row.currency).first()
                if account is None:
                    account = Account(id=uuid4(), user_id=session.user_id, name=row.account.casefold(), currency=row.currency, type="bank")
                    db.add(account)
                    db.flush()
                tx = Transaction(id=uuid4(), user_id=session.user_id, account_id=account.id, amount=row.amount,
                                 type=row.transaction_type, category=row.category, description=row.description, occurred_at=row.date)
                db.add(tx)
                db.flush()
                db.add(ImportedTransaction(session_id=session.id, batch_id=batch.id, transaction_id=tx.id,
                                          fingerprint=key, source_row=row.source_row,
                                          balance_optional=str(row.balance_optional) if row.balance_optional is not None else None))
                existing.add(key)
                committed_rows.append(row.model_dump(mode="json"))
                imported += 1
            result = ConfirmResponse(batch_id=batch.id, imported=imported, duplicates=duplicates,
                                     skipped_invalid=reviewed.invalid, excluded=reviewed.excluded,
                                     message=f"{imported:,} transactions imported successfully.")
            batch.status, batch.tables, batch.review = "committed", None, None
            batch.result = result.model_dump(mode="json")
            # Existing JSON provenance storage: no production schema migration required.
            # Retained only until the owning demo session expires or is deleted.
            batch.result["provenance"] = committed_rows
            batch.result["reconciliation"] = reviewed.reconciliation.model_dump(mode="json")
            return result
    except IntegrityError:
        raise HTTPException(409, "Another import changed these rows. Validate again before confirming.") from None


@router.get("/analytics", response_model=DashboardSummary)
def analytics(month: str | None = Query(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
              currency: str | None = Query(default=None, pattern=r"^[A-Z]{3}$"),
              x_demo_session: str | None = Header(default=None)):
    with SessionLocal() as db:
        user_id = require_session(db, x_demo_session).user_id
    try:
        return DashboardViewModel.get_summary(user_id, month=month, currency=currency)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
