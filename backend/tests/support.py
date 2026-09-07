"""Small isolated SQLite harness; never reads or connects to the user's database."""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["FRONTEND_URLS"] = "http://localhost:5173"
os.environ["LOCAL_DEMO"] = "true"

from uuid import uuid4
from unittest import TestCase
from unittest.mock import patch
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.database.base import Base
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.views import dashboard_view, transactions_view


class DatabaseCase(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        @event.listens_for(self.engine, "connect")
        def foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine)
        self.patches = [patch(f"app.viewmodels.{name}.SessionLocal", self.sessions)
                        for name in ["dashboard_vm", "transactions_vm", "accounts_vm"]]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.engine.dispose)
        app = FastAPI()
        app.include_router(dashboard_view.router)
        app.include_router(transactions_view.router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def user_account(self, currency="ZAR"):
        user_id, account_id = uuid4(), uuid4()
        with self.sessions.begin() as db:
            db.add(User(id=user_id, email=f"{user_id}@example.invalid", password_hash="!test-disabled!"))
            db.flush()
            db.add(Account(id=account_id, user_id=user_id, name="Test account", type="bank", currency=currency))
        return user_id, account_id
