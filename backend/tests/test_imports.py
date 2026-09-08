"""Synthetic, isolated import regression tests: never connect to a user's database."""
import io
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from unittest import TestCase
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from support import DatabaseCase
from app.schemas.imports import ReviewRequest
from app.services.file_parser import parse_file, parse_bounded, detect_header, detect_mapping, PDF_ERROR
from app.services.import_normalization import decimal_value, normalized_date, normalize_rows
from app.models.imports import DemoSession, ImportBatch, ImportedTransaction
from app.models.transaction import Transaction
from app.services.import_sessions import cleanup_expired
from app.views import import_view

FIXTURES = Path(__file__).parent / "fixtures"


class ParsingTests(TestCase):
    def test_semicolon_csv_with_title_and_decimal_comma(self):
        raw = 'Synthetic export\nDate;Description;Amount\n02/08/2026;Synthetic cafe;-123,45\n'.encode()
        _, tables = parse_file(raw, 'semicolon.csv')
        self.assertEqual(detect_header(tables['CSV']), 2)
        self.assertEqual(tables['CSV'][2][2], '-123,45')

    def test_csv_and_formats(self):
        for name in ["standard.csv", "standard.xlsx", "standard.xls", "standard.ods", "synthetic_statement.pdf"]:
            with self.subTest(name=name):
                kind, tables = parse_file((FIXTURES / name).read_bytes(), name)
                self.assertEqual(kind, name.split(".")[-1])
                self.assertEqual(len(next(iter(tables.values()))), 5)

    def test_sheet_and_header_detection(self):
        _, tables = parse_file((FIXTURES / "renamed_headers.xlsx").read_bytes(), "book.xlsx")
        self.assertEqual(list(tables), ["Notes", "Transactions"])
        self.assertEqual(detect_header(tables["Transactions"]), 3)
        mapped = detect_mapping(tables["Transactions"][2])
        self.assertEqual(mapped["description"]["column"], 1)
        self.assertEqual(mapped["balance"]["column"], 3)
        self.assertTrue(tables["Transactions"][3][0].startswith("2026-08-01"))

    def test_ambiguous_mapping_is_not_guessed(self):
        mapped = detect_mapping(["DATE", " Posting-Date ", "Narrative", "VALUE"])
        self.assertIsNone(mapped["date"]["column"])
        self.assertEqual(mapped["date"]["confidence"], "ambiguous")
        self.assertEqual(mapped["description"]["confidence"], "high")

    def test_invalid_file_signatures_and_limits(self):
        for content, name in [(b"abc", "file.xls"), (b"abc", "file.xlsb"), (b"%PDF", "file.csv"),
                              (b"abc", "file.exe"), (b"", "file.csv"), (b"x" * (5 * 1024 * 1024 + 1), "file.csv")]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                parse_file(content, name)

    def test_scanned_pdf_rejected(self):
        from reportlab.pdfgen import canvas
        output = io.BytesIO()
        page = canvas.Canvas(output)
        page.rect(20, 20, 100, 100)
        page.showPage()
        page.save()
        with self.assertRaisesRegex(ValueError, "cannot reliably read"):
            parse_file(output.getvalue(), "scan.pdf")

    def test_text_pdf_without_reliable_table_rejected(self):
        from reportlab.pdfgen import canvas
        output = io.BytesIO()
        page = canvas.Canvas(output)
        page.drawString(20, 700, "Date Description Amount 2026-08-01 Ambiguous 100")
        page.save()
        with self.assertRaises(ValueError):
            parse_file(output.getvalue(), "loose.pdf")

    def test_bounded_parser_and_timeout(self):
        self.assertEqual(parse_bounded((FIXTURES / "standard.csv").read_bytes(), "x.csv")[0], "csv")
        import subprocess
        with patch("app.services.file_parser.subprocess.run", side_effect=subprocess.TimeoutExpired("parser", 20)):
            with self.assertRaisesRegex(ValueError, "20 seconds"):
                parse_bounded(b"a", "x.csv")

    def test_decimal_formats_precision_and_currency(self):
        for raw, fmt, currency, expected in [("R 1,234.56", "dot", "ZAR", "1234.56"),
                ("1.234,56", "comma", "EUR", "1234.56"), ("EUR 12.30", "dot", "EUR", "12.30"),
                ("(123.45)", "dot", "ZAR", "-123.45"), ("1 234,56", "comma", "ZAR", "1234.56"),
                ("0.10", "dot", "ZAR", "0.10"), (0, "dot", "ZAR", "0.00"),
                ("-R123.45", "dot", "ZAR", "-123.45"), ("(R 123.45)", "dot", "ZAR", "-123.45")]:
            self.assertEqual(decimal_value(raw, fmt, currency), Decimal(expected))
        for raw in ["1.234", "NaN", "1,23.00", "", "=1+1", "EUR 5", "1e3"]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                decimal_value(raw, "dot", "ZAR")
        self.assertEqual(decimal_value("0.10", "dot", "ZAR") + decimal_value("0.20", "dot", "ZAR"), Decimal("0.30"))

    def test_explicit_dates(self):
        self.assertEqual(normalized_date("02/08/2026", "DMY"), datetime(2026, 8, 2))
        self.assertEqual(normalized_date("02/08/2026", "MDY"), datetime(2026, 2, 8))
        self.assertEqual(normalized_date("2026-08-02", "YMD"), datetime(2026, 8, 2))
        self.assertEqual(normalized_date("46236", "DMY"), datetime(2026, 8, 2))
        with self.assertRaises(ValueError):
            normalized_date("31/02/2026", "DMY")


class ImportAPITests(DatabaseCase):
    def setUp(self):
        super().setUp()
        p = patch("app.views.import_view.SessionLocal", self.sessions)
        p.start()
        self.addCleanup(p.stop)
        app = FastAPI()
        app.include_router(import_view.router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.headers = self.session()

    def session(self):
        response = self.client.post("/imports/session")
        self.assertEqual(response.status_code, 201, response.text)
        return {"X-Demo-Session": response.json()["token"]}

    def upload(self, name, headers=None):
        response = self.client.post("/imports/upload", content=(FIXTURES / name).read_bytes(),
                                    headers={**(headers or self.headers), "X-File-Name": name})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def review(self, upload, headers=None, **changes):
        options = dict(sheet=upload["sheet"], header_row=upload["header_row"],
                       mapping={k: v["column"] for k, v in upload["mapping"].items()},
                       account="Everyday", currency="ZAR", date_order="DMY", number_format="dot",
                       sign_convention="negative_expense")
        options.update(changes)
        response = self.client.post(f"/imports/{upload['batch_id']}/review", json=options, headers=headers or self.headers)
        return response

    def confirm(self, reviewed, headers=None, **changes):
        return self.client.post(f"/imports/{reviewed['batch_id']}/confirm",
                                json={"review_id": reviewed["review_id"], "confirmed": True, **changes},
                                headers=headers or self.headers)

    def test_three_source_totals_reconcile_with_existing_analytics(self):
        # Independently specified from the fixture ledger, not computed with importer helpers.
        for name, count, income, expenses, net in [
            ("standard.csv", 4, "1000.00", "250.00", "750.00"),
            ("debit_credit.csv", 3, "2000.00", "625.00", "1375.00"),
            ("renamed_headers.xlsx", 4, "3000.00", "699.99", "2300.01"),
        ]:
            with self.subTest(name=name):
                headers = self.session()
                uploaded = self.upload(name, headers)
                reviewed_response = self.review(uploaded, headers)
                self.assertEqual(reviewed_response.status_code, 200, reviewed_response.text)
                reviewed = reviewed_response.json()
                self.assertEqual((reviewed["detected"], reviewed["invalid"], reviewed["to_import"]), (count, 0, count))
                self.assertEqual((reviewed["income"], reviewed["expenses"], reviewed["net_cash_flow"]), (income, expenses, net))
                result = self.confirm(reviewed, headers)
                self.assertEqual(result.status_code, 200, result.text)
                self.assertEqual(result.json()["imported"], count)
                data = self.client.get("/imports/analytics?month=2026-08", headers=headers).json()
                self.assertEqual((data["selected"]["income"], data["selected"]["expenses"], data["selected"]["net_cash_flow"]), (income, expenses, net))
                self.assertEqual(data["trends"]["spending"]["total_expenses"], expenses)
                self.assertEqual(data["net_worth"]["status"], "unavailable")

    def test_duplicates_and_confirm_idempotency(self):
        first = self.review(self.upload("duplicates.csv")).json()
        # No reference/balance proves the repeated purchase is a duplicate.
        self.assertEqual((first["duplicates"], first["to_import"]), (0, 5))
        self.assertEqual(self.confirm(first).json()["imported"], 5)
        self.assertEqual(self.confirm(first).json()["imported"], 5)
        second = self.review(self.upload("standard.csv")).json()
        self.assertEqual((second["duplicates"], second["to_import"]), (4, 0))
        self.assertEqual(self.confirm(second).json()["imported"], 0)
        with self.sessions() as db:
            self.assertEqual(db.query(Transaction).count(), 5)
            batch = db.get(ImportBatch, __import__("uuid").UUID(first["batch_id"]))
            self.assertIsNone(batch.tables)
            self.assertIsNone(batch.review)

    def test_user_isolation_and_no_unauthorized_batch_access(self):
        uploaded = self.upload("standard.csv")
        other = self.session()
        self.assertEqual(self.review(uploaded, other).status_code, 404)
        first = self.review(uploaded).json()
        self.assertEqual(self.confirm(first, other).status_code, 404)
        self.confirm(first)
        data = self.client.get("/imports/analytics", headers=other).json()
        self.assertEqual(data["selected"]["transaction_count"], 0)
        second = self.review(self.upload("standard.csv", other), other).json()
        self.assertEqual(second["duplicates"], 0)
        self.assertEqual(self.client.get("/imports/analytics").status_code, 401)

    def test_currency_isolation(self):
        self.confirm(self.review(self.upload("standard.csv")).json())
        usd = self.review(self.upload("standard.csv"), currency="USD").json()
        self.assertEqual(usd["duplicates"], 0)
        self.confirm(usd)
        for code in ["ZAR", "USD"]:
            data = self.client.get(f"/imports/analytics?currency={code}", headers=self.headers).json()
            self.assertEqual(data["selected"]["income"], "1000.00")
            self.assertEqual(data["selected"]["transaction_count"], 4)

    def test_validation_and_manual_mapping(self):
        missing = self.review(self.upload("missing_column.csv"))
        self.assertEqual(missing.status_code, 422)
        malformed = self.review(self.upload("malformed.csv")).json()
        self.assertEqual(malformed["invalid"], 2)
        self.assertEqual(self.confirm(malformed).status_code, 422)
        manual = self.review(self.upload("manual.csv"), mapping={"date": 0, "description": 1, "amount": 2}).json()
        self.assertEqual(manual["income"], "800.10")
        self.assertEqual(manual["invalid"], 0)

    def test_sign_convention_and_transfer_override(self):
        reviewed = self.review(self.upload("positive_expense.csv"), sign_convention="positive_expense").json()
        self.assertEqual((reviewed["income"], reviewed["expenses"]), ("1500.00", "123.45"))
        uploaded = self.upload("standard.csv")
        reviewed = self.review(uploaded, type_overrides={"3": "transfer"}).json()
        self.assertEqual(reviewed["expenses"], "50.00")

    def test_stale_review_requires_revalidation(self):
        uploaded = self.upload("standard.csv")
        old = self.review(uploaded).json()
        new = self.review(uploaded, excluded_rows=[3]).json()
        self.assertEqual(self.confirm(old).status_code, 409)
        self.assertEqual(self.confirm(new).json()["imported"], 3)

    def test_pdf_uses_same_normalization(self):
        reviewed = self.review(self.upload("synthetic_statement.pdf")).json()
        self.assertEqual((reviewed["income"], reviewed["expenses"], reviewed["to_import"]), ("1000.00", "250.00", 4))
        self.assertEqual(self.confirm(reviewed).json()["imported"], 4)

    def test_expiry_and_delete_only_owned_records(self):
        unrelated, _ = self.user_account()
        self.confirm(self.review(self.upload("standard.csv")).json())
        with self.sessions.begin() as db:
            session = db.query(DemoSession).one()
            session.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1)
        self.assertEqual(self.client.get("/imports/analytics", headers=self.headers).status_code, 401)
        with self.sessions.begin() as db:
            cleanup_expired(db)
            self.assertEqual(db.query(ImportedTransaction).count(), 0)
            self.assertEqual(db.query(Transaction).count(), 0)
            from app.models.user import User
            self.assertIsNotNone(db.get(User, unrelated))
        self.headers = self.session()
        self.confirm(self.review(self.upload("standard.csv")).json())
        self.assertEqual(self.client.delete("/imports/session", headers=self.headers).status_code, 204)
        self.assertEqual(self.client.get("/imports/analytics", headers=self.headers).status_code, 401)

    def test_public_surface_omits_legacy_user_routes(self):
        from app.demo_app import create_demo_app
        app = create_demo_app()
        paths = {route.path for route in app.routes}
        self.assertIn("/imports/analytics", paths)
        self.assertIn("/dashboard/demo", paths)
        self.assertNotIn("/dashboard/{user_id}", paths)
        self.assertFalse(any(path.startswith(("/users", "/transactions", "/auth")) for path in paths))

    def test_debit_credit_row_errors_and_explicit_skip(self):
        raw = b'Date,Description,Debit,Credit\n2026-08-01,Valid debit,12.30,\n2026-08-02,Both,5,5\n2026-08-03,Negative,-5,\n2026-08-04,Blank,,\n'
        response = self.client.post('/imports/upload', content=raw, headers={**self.headers, 'X-File-Name': 'rows.csv'})
        reviewed = self.review(response.json()).json()
        self.assertEqual((reviewed['invalid'], reviewed['to_import'], reviewed['expenses']), (3, 1, '12.30'))
        self.assertEqual(self.confirm(reviewed).status_code, 422)
        self.assertEqual(self.confirm(reviewed, skip_invalid=True).json()['skipped_invalid'], 3)
        self.assertEqual(self.client.get('/imports/analytics', headers=self.headers).json()['selected']['expenses'], '12.30')

    def test_mixed_currency_row_is_invalid(self):
        raw = b'Date,Description,Amount,Currency\n2026-08-01,A,20,ZAR\n2026-08-02,B,30,USD\n'
        response = self.client.post('/imports/upload', content=raw, headers={**self.headers, 'X-File-Name': 'mixed.csv'})
        reviewed = self.review(response.json()).json()
        self.assertEqual((reviewed['to_import'], reviewed['invalid'], reviewed['income']), (1, 1, '20.00'))

    def test_unknown_type_can_be_reviewed_with_override(self):
        raw = b'Date,Description,Amount,Type\n2026-08-01,A,-20,internal move\n'
        uploaded = self.client.post('/imports/upload', content=raw, headers={**self.headers, 'X-File-Name': 'type.csv'}).json()
        self.assertEqual(self.review(uploaded).json()['invalid'], 1)
        reviewed = self.review(uploaded, type_overrides={'2': 'transfer'}).json()
        self.assertEqual((reviewed['invalid'], reviewed['income'], reviewed['expenses']), (0, '0.00', '0.00'))

    def test_preview_expiry_discards_source_rows(self):
        uploaded = self.upload('standard.csv')
        with self.sessions.begin() as db:
            batch = db.get(ImportBatch, __import__('uuid').UUID(uploaded['batch_id']))
            batch.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1)
            cleanup_expired(db)
            self.assertIsNone(batch.tables)
        self.assertEqual(self.review(uploaded).status_code, 409)

    def test_detect_selected_sheet_and_reject_invalid_header(self):
        uploaded = self.upload('renamed_headers.xlsx')
        response = self.client.post(f"/imports/{uploaded['batch_id']}/detect", json={'sheet': 'Transactions'}, headers=self.headers)
        self.assertEqual(response.json()['header_row'], 3)
        response = self.client.post(f"/imports/{uploaded['batch_id']}/detect", json={'sheet': 'Notes', 'header_row': 20}, headers=self.headers)
        self.assertEqual(response.status_code, 422)

    def test_amount_and_debit_mapping_cannot_be_combined(self):
        uploaded = self.upload('renamed_headers.xlsx')
        response = self.review(uploaded, mapping={'date': 0, 'description': 1, 'amount': 2, 'debit': 3})
        self.assertEqual(response.status_code, 422)

    def test_public_postgres_guard_and_ddl(self):
        from app.demo_app import create_demo_app
        from app.core.config import settings
        from app.database.base import Base
        from sqlalchemy.schema import CreateTable
        from sqlalchemy.dialects import postgresql
        with patch.object(settings, 'local_demo', False), patch.object(settings, 'database_url', 'sqlite://'):
            with self.assertRaisesRegex(RuntimeError, 'PostgreSQL'):
                create_demo_app()
        with patch.object(settings, 'cors_allowed_origins', '*'):
            with self.assertRaisesRegex(RuntimeError, 'CORS_ALLOWED_ORIGINS'):
                create_demo_app()
        for table in Base.metadata.sorted_tables:
            self.assertIn('CREATE TABLE', str(CreateTable(table).compile(dialect=postgresql.dialect())))
