from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch
from support import DatabaseCase
from app.models.account import Account
from app.models.transaction import Transaction
from app.core.config import settings
from scripts.seed_demo import DEMO_USER_ID, seed_demo


class DashboardApiTests(DatabaseCase):
    def test_serialized_financial_contract(self):
        user, account = self.user_account()
        with self.sessions.begin() as db:
            for amount, kind in [("0.10", "income"), ("0.20", "income"), ("0.10", "expense"), ("900", "transfer")]:
                db.add(Transaction(user_id=user, account_id=account, amount=Decimal(amount), type=kind, occurred_at=datetime(2026, 8, 1)))
        response = self.client.get(f"/dashboard/{user}?month=2026-08&currency=ZAR")
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["selected"]["income"], "0.30")
        self.assertEqual(result["selected"]["net_cash_flow"], "0.20")
        self.assertEqual(result["selected"]["savings_rate"], "66.67")
        self.assertEqual(len(result["history"]), 12)
        self.assertIsNone(result["net_worth"]["value"])
        self.assertIsNone(result["account_balances"][0]["value"])

    def test_database_user_and_currency_isolation(self):
        first, account = self.user_account()
        second, other = self.user_account()
        usd = uuid4()
        with self.sessions.begin() as db:
            db.add(Account(id=usd, user_id=first, name="USD", type="bank", currency="USD"))
            db.flush()
            for owner, acc, amount in [(first, account, "10"), (second, other, "999"), (first, usd, "30")]:
                db.add(Transaction(user_id=owner, account_id=acc, amount=Decimal(amount), type="income", occurred_at=datetime(2026, 8, 1)))
        result = self.client.get(f"/dashboard/{first}?month=2026-08&currency=ZAR").json()
        self.assertEqual(result["selected"]["income"], "10.00")
        self.assertEqual(result["available_currencies"], ["USD", "ZAR"])
        self.assertEqual(self.client.get(f"/dashboard/{first}?month=2026-08&currency=USD").json()["selected"]["income"], "30.00")

    def test_invalid_parameters(self):
        for query in ["month=bad", "month=2026-13", "month=0000-01", "month=0002-01", "month=9999-12", "currency=INVALID"]:
            with self.subTest(query=query):
                self.assertEqual(self.client.get(f"/dashboard/{uuid4()}?{query}").status_code, 422)

    def test_empty_user_has_twelve_zero_months(self):
        result = self.client.get(f"/dashboard/{uuid4()}?month=2026-08").json()
        self.assertEqual(len(result["history"]), 12)
        self.assertEqual(result["selected"]["income"], "0.00")
        self.assertIsNone(result["selected"]["savings_rate"])
        self.assertEqual(result["account_balances"], [])

    def test_demo_uses_same_service_and_is_opt_in(self):
        with self.sessions.begin() as db:
            seed_demo(db)
        demo = self.client.get("/dashboard/demo?month=2026-08").json()
        real = self.client.get(f"/dashboard/{DEMO_USER_ID}?month=2026-08").json()
        self.assertTrue(demo.pop("demo"))
        self.assertFalse(real.pop("demo"))
        self.assertEqual(demo, real)
        with patch.object(settings, "local_demo", False):
            self.assertEqual(self.client.get("/dashboard/demo").status_code, 404)
