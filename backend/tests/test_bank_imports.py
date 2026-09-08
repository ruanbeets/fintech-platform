"""Bank-format hardening using a fully synthetic ledger and literal expected totals."""
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from unittest import TestCase
import test_imports
from support import DatabaseCase
from app.schemas.imports import ReviewRequest
from app.services.file_parser import parse_file, detect_header, detect_mapping
from app.services.import_detection import suggestions
from app.services.import_normalization import normalize_rows, fingerprint
from app.services.import_reconciliation import reconcile
from app.models.imports import ImportBatch

FIXTURES = Path(__file__).parent / "fixtures"


def normalize(table, **changes):
    header = detect_header(table)
    mapping = detect_mapping(table[header-1])
    defaults, _ = suggestions(table, header, mapping)
    args = dict(sheet="CSV", header_row=header, mapping={k: v["column"] for k, v in mapping.items()},
                account="Synthetic account", currency="ZAR", **defaults)
    args.update(changes)
    return normalize_rows(table, ReviewRequest(**args), uuid4(), "synthetic.csv", set())


class BankNormalizationTests(TestCase):
    def test_distinct_dates_and_single_date_fallback(self):
        mapped = detect_mapping(["Posting Date", "Transaction Date", "Description", "Money In", "Money Out", "Fee"])
        self.assertEqual((mapped["date"]["column"], mapped["transaction_datetime"]["column"]), (0, 1))
        single = detect_mapping(["Transaction Date", "Description", "Amount"])
        self.assertEqual(single["date"]["column"], 0)
        self.assertIsNone(single["transaction_datetime"]["column"])

    def test_reference_preserves_dates_categories_fees_direction_and_accounts(self):
        _, tables = parse_file((FIXTURES / "bank_reference.csv").read_bytes(), "bank.csv")
        result = normalize(tables["CSV"])
        rows = [r.transaction for r in result if r.transaction]
        self.assertEqual(rows[0].booking_date.isoformat(), "2026-08-01T00:00:00")
        self.assertEqual(rows[0].transaction_datetime.isoformat(), "2026-07-31T00:00:00")
        self.assertEqual(rows[0].original_description, "PAYROLL SYNTHETIC")
        self.assertEqual((rows[2].signed_amount, rows[2].fee_amount), (Decimal("-3.00"), Decimal("3.00")))
        self.assertEqual((rows[3].direction, rows[3].transaction_type), ("CREDIT", "transfer"))
        self.assertEqual((rows[4].direction, rows[4].transaction_type), ("DEBIT", "transfer"))
        self.assertEqual((rows[3].source_parent_category, rows[3].source_category), ("Transfers", "Savings"))
        self.assertNotIn("0000123400", rows[0].model_dump_json())
        self.assertEqual(result[-1].status, "invalid")
        self.assertIn("no amount", result[-1].errors[0])

    def test_exact_and_failed_reconciliation_and_reverse_signs(self):
        table = [["Date", "Description", "Amount", "Balance"], ["2026-08-01", "A", "100", "1100"],
                 ["2026-08-02", "B", "-20", "1080"], ["2026-08-03", "C", "-30", "1050"]]
        checked = reconcile(normalize(table))
        self.assertEqual((checked.status, checked.rows_matched, checked.confidence), ("RECONCILED", 2, "high"))
        reversed_sign = reconcile(normalize(table, sign_convention="positive_expense"))
        self.assertTrue(reversed_sign.probable_sign_error)
        self.assertEqual(reversed_sign.rows_failed, 2)
        table[-1][-1] = "1040"
        failed = reconcile(normalize(table))
        self.assertEqual((failed.rows_failed, failed.maximum_difference, failed.failed_rows), (1, Decimal("10.00"), [4]))

    def test_descending_and_same_day_balance_sequence(self):
        table = [["Date", "Description", "Amount", "Balance"], ["2026-08-02", "Cafe", "-20", "1060"],
                 ["2026-08-02", "Cafe", "-20", "1080"], ["2026-08-01", "Pay", "100", "1100"]]
        checked = reconcile(normalize(table))
        self.assertEqual((checked.order, checked.rows_matched), ("descending", 2))

    def test_missing_row_does_not_bridge_balance_gap(self):
        table = [["Date", "Description", "Amount", "Balance"], ["2026-08-01", "A", "100", "1100"],
                 ["bad-date", "B", "-20", "1080"], ["2026-08-03", "C", "-30", "1050"]]
        checked = reconcile(normalize(table))
        self.assertEqual(checked.rows_tested, 0)
        self.assertEqual(checked.skipped_rows, [3])

    def test_no_balance_and_repeated_purchases_retained(self):
        table = [["Date", "Description", "Amount"], ["2026-08-01", "Cafe", "-20"], ["2026-08-01", "Cafe", "-20"]]
        result = normalize(table)
        self.assertEqual([r.status for r in result], ["valid", "valid"])
        self.assertNotEqual(fingerprint(result[0].transaction), fingerprint(result[1].transaction))
        self.assertEqual(reconcile(result).status, "UNAVAILABLE")

    def test_semantic_override_does_not_change_duplicate_identity(self):
        table = [["Date", "Description", "Amount"], ["2026-08-01", "Payment", "-20"]]
        ordinary = normalize(table)[0].transaction
        transfer = normalize(table, type_overrides={2: "transfer"})[0].transaction
        self.assertEqual(fingerprint(ordinary), fingerprint(transfer))

    def test_credit_type_does_not_erase_explicit_transfer_category(self):
        table = [["Date", "Description", "Amount", "Category", "Type"], ["2026-08-01", "Transfer", "20", "Transfers", "credit"]]
        self.assertEqual(normalize(table)[0].transaction.transaction_type, "transfer")

    def test_invalid_combined_range_and_sign_markers(self):
        table = [["Date", "Description", "Money Out", "Fee"], ["2026-08-01", "Payment", "-999999999999", "-3"]]
        self.assertEqual(normalize(table)[0].status, "invalid")
        table = [["Date", "Description", "Amount"], ["2026-08-01", "Payment", "(-20)"]]
        self.assertEqual(normalize(table)[0].status, "invalid")

    def test_source_reference_identifies_duplicate(self):
        table = [["Date", "Description", "Amount", "Transaction ID"], ["2026-08-01", "Cafe", "-20", "synthetic-1"],
                 ["2026-08-01", "Cafe", "-20", "synthetic-1"]]
        self.assertEqual([r.status for r in normalize(table)], ["valid", "duplicate"])

    def test_fee_not_added_twice_to_signed_amount(self):
        table = [["Date", "Description", "Amount", "Fee"], ["2026-08-01", "Payment", "-103", "-3"]]
        row = normalize(table)[0].transaction
        self.assertEqual((row.amount, row.fee_amount), (Decimal("103.00"), Decimal("3.00")))

    def test_separate_fee_combines_once_with_money_out(self):
        table = [["Date", "Description", "Money In", "Money Out", "Fee"], ["2026-08-01", "Payment", "", "-100", "-3"]]
        self.assertEqual(normalize(table)[0].transaction.signed_amount, Decimal("-103.00"))

    def test_metadata_repeated_header_and_balance_summaries(self):
        table = [["Date", "Description", "Amount", "Balance"], ["2026-08-01", "Opening balance", "1000", "1000"],
                 ["2026-08-02", "Cafe", "-20", "980"], ["Date", "Description", "Amount", "Balance"],
                 ["2026-08-31", "Closing balance", "980", "980"]]
        self.assertEqual([r.status for r in normalize(table)], ["excluded", "valid", "excluded", "excluded"])

    def test_ambiguous_dates_do_not_get_high_confidence(self):
        table = [["Date", "Description", "Amount"], ["01/02/2026", "Cafe", "-20"]]
        _, high = suggestions(table, 1, detect_mapping(table[0]))
        self.assertFalse(high)

    def test_account_and_currency_reconciliation_isolation(self):
        table = [["Date", "Description", "Amount", "Balance", "Account"], ["2026-08-01", "A", "100", "1100", "001"],
                 ["2026-08-02", "B", "-20", "980", "002"], ["2026-08-03", "C", "-30", "1070", "001"]]
        checked = reconcile(normalize(table))
        self.assertEqual((checked.rows_tested, checked.rows_matched), (1, 1))
        self.assertNotEqual(normalize(table)[0].transaction.account, normalize(table)[1].transaction.account)


class BankAPIHardeningTests(DatabaseCase):
    # Reuse just the existing API helpers; regression tests run in their own module.
    session = test_imports.ImportAPITests.session
    upload = test_imports.ImportAPITests.upload
    review = test_imports.ImportAPITests.review
    confirm = test_imports.ImportAPITests.confirm

    def setUp(self):
        from unittest.mock import patch
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.views import import_view
        super().setUp()
        patched = patch("app.views.import_view.SessionLocal", self.sessions)
        patched.start()
        self.addCleanup(patched.stop)
        app = FastAPI()
        app.include_router(import_view.router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.headers = self.session()
    def test_six_fixture_ledgers_and_imported_analytics(self):
        for name in ["bank_signed.csv", "bank_debit_credit.csv", "bank_money.csv", "bank_reference.csv", "bank_european.csv", "bank_tab.csv"]:
            with self.subTest(name=name):
                headers = self.session()
                detected = self.upload(name, headers)
                self.assertNotIn("0000123400", str(detected["preview"]))
                checked = self.review(detected, headers, **detected["defaults"])
                self.assertEqual(checked.status_code, 200, checked.text)
                reviewed = checked.json()
                rows = [r["transaction"] for r in reviewed["rows"] if r["transaction"]]
                # Literal ledger: credits 3000 + 200, debits 500 + 3 + 400 + 25 + 25.
                self.assertEqual(len(rows), 7)
                self.assertEqual(sum(Decimal(r["signed_amount"]) for r in rows if r["direction"] == "CREDIT"), Decimal("3200.00"))
                self.assertEqual(sum(-Decimal(r["signed_amount"]) for r in rows if r["direction"] == "DEBIT"), Decimal("953.00"))
                self.assertEqual(sum(Decimal(r["fee_amount"] or "0") for r in rows), Decimal("3.00"))
                self.assertEqual(sum(Decimal(r["amount"]) for r in rows if r["transaction_type"] == "transfer"), Decimal("600.00"))
                self.assertEqual(sum(Decimal(r["signed_amount"]) for r in rows), Decimal("2247.00"))
                self.assertEqual(rows[-1]["balance_optional"], "3247.00")
                self.assertEqual(reviewed["reconciliation"]["rows_matched"], 6)
                self.assertEqual((reviewed["income"], reviewed["expenses"], reviewed["net_cash_flow"]), ("3000.00", "553.00", "2447.00"))
                self.assertEqual(self.confirm(reviewed, headers, skip_invalid=True).json()["imported"], 7)
                api = self.client.get("/imports/analytics?month=2026-08", headers=headers).json()
                self.assertEqual((api["selected"]["income"], api["selected"]["expenses"], api["selected"]["net_cash_flow"]), ("3000.00", "553.00", "2447.00"))
                self.assertEqual(api["trends"]["spending"]["total_expenses"], "553.00")
                again = self.upload(name, headers)
                repeated = self.review(again, headers, **again["defaults"]).json()
                self.assertEqual((repeated["duplicates"], repeated["to_import"]), (7, 0))
                with self.sessions() as db:
                    provenance = db.get(ImportBatch, __import__("uuid").UUID(reviewed["batch_id"])).result["provenance"]
                    self.assertEqual(len(provenance), 7)
                    self.assertNotIn("0000123400", str(provenance))
