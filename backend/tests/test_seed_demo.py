from datetime import date, datetime
from decimal import Decimal as D
from uuid import uuid4
from support import DatabaseCase
from app.models.account import Account
from app.models.transaction import Transaction
from scripts.seed_demo import seed_demo, transaction_rows, DEMO_USER_ID


class SeedDemoTests(DatabaseCase):
    def test_repeatability_and_unrelated_records_preserved(self):
        user, account = self.user_account()
        unrelated = uuid4()
        with self.sessions.begin() as db:
            db.add(Transaction(id=unrelated, user_id=user, account_id=account, amount=D("123.45"),
                               type="income", occurred_at=datetime(2026, 1, 1)))
            first = seed_demo(db)
        with self.sessions.begin() as db:
            before = [(t.id, t.amount, t.type, t.occurred_at) for t in db.query(Transaction).order_by(Transaction.id)]
            self.assertEqual(seed_demo(db), 0)
            after = [(t.id, t.amount, t.type, t.occurred_at) for t in db.query(Transaction).order_by(Transaction.id)]
            self.assertEqual(before, after)
            self.assertEqual(db.get(Transaction, unrelated).amount, D("123.45"))
            self.assertEqual(db.get(Account, account).user_id, user)
        self.assertEqual(first, len(list(transaction_rows())))

    def test_fixture_coverage_categories_variation_and_owner(self):
        rows = list(transaction_rows())
        months = {r["occurred_at"].strftime("%Y-%m") for r in rows}
        self.assertEqual(len(months), 23)
        self.assertEqual((min(months), max(months)), ("2024-09", "2026-08"))
        self.assertNotIn("2025-11", months)
        self.assertEqual({r["user_id"] for r in rows}, {DEMO_USER_ID})
        self.assertEqual({r["type"] for r in rows}, {"income", "expense", "transfer"})
        self.assertGreaterEqual(len({r["category"] for r in rows}), 10)
        self.assertEqual(rows, list(transaction_rows()))
        with self.sessions.begin() as db:
            seed_demo(db)
            self.assertEqual({a.currency for a in db.query(Account).filter(Account.user_id == DEMO_USER_ID)}, {"ZAR"})

    def test_two_months_match_independent_expected_figures(self):
        # Independently itemized expenses (housing, utilities, insurance, fibre,
        # transport, dining, health, four groceries, and any irregular expense).
        examples = {
            "2026-08": (D("42000"), sum(map(D, ["11850", "1635", "890.50", "749", "1910", "1445", "710", "969.45", "1032.45", "780.45", "843.45"])), D("45.68")),
            "2025-12": (D("54000"), sum(map(D, ["11850", "1635", "890.50", "749", "1550", "980", "710", "780.45", "843.45", "906.45", "969.45", "8200"])), D("44.33")),
        }
        with self.sessions.begin() as db:
            seed_demo(db)
        for month, (income, expenses, savings_rate) in examples.items():
            with self.subTest(month=month):
                rows = [r for r in transaction_rows() if r["occurred_at"].strftime("%Y-%m") == month]
                self.assertEqual(sum((r["amount"] for r in rows if r["type"] == "income"), D("0")), income)
                self.assertEqual(sum((r["amount"] for r in rows if r["type"] == "expense"), D("0")), expenses)
                result = self.client.get(f"/dashboard/demo?month={month}").json()["selected"]
                self.assertEqual(D(result["income"]), income)
                self.assertEqual(D(result["expenses"]), expenses)
                self.assertEqual(D(result["net_cash_flow"]), income - expenses)
                self.assertEqual(D(result["savings_rate"]), savings_rate)
