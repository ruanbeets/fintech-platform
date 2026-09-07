"""Short-lived capability sessions, with deletion restricted to their dedicated users."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import HTTPException
from app.core.config import settings
from app.models.imports import DemoSession, ImportBatch, ImportedTransaction
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


def create_session(db):
    token = secrets.token_urlsafe(32)
    user_id = uuid4()
    db.add(User(id=user_id, email=f"{user_id}@import-demo.invalid", password_hash="!anonymous-disabled!"))
    db.flush()
    session = DemoSession(user_id=user_id, token_hash=hashlib.sha256(token.encode()).hexdigest(),
                          expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=settings.session_hours))
    db.add(session)
    db.flush()
    return {"token": token, "expires_at": session.expires_at.isoformat() + "Z"}


def require_session(db, token, lock=False):
    if not token or len(token) > 100:
        raise HTTPException(401, "Start a new import session.")
    query = db.query(DemoSession).filter_by(token_hash=hashlib.sha256(token.encode()).hexdigest())
    session = query.with_for_update().first() if lock else query.first()
    if session is None or session.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(401, "This demo session has expired. Start a new import session.")
    return session


def delete_session(db, session):
    db.query(ImportedTransaction).filter_by(session_id=session.id).delete()
    db.query(ImportBatch).filter_by(session_id=session.id).delete()
    db.query(Transaction).filter_by(user_id=session.user_id).delete()
    db.query(Account).filter_by(user_id=session.user_id).delete()
    user_id = session.user_id
    db.delete(session)
    db.flush()
    db.query(User).filter_by(id=user_id).delete()


def cleanup_expired(db):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for session in db.query(DemoSession).filter(DemoSession.expires_at <= now).with_for_update().all():
        delete_session(db, session)
    # Pending previews contain source rows; retain for at most one hour.
    for batch in db.query(ImportBatch).filter(ImportBatch.status == "pending", ImportBatch.expires_at <= now).all():
        batch.tables, batch.review, batch.status = None, None, "expired"
