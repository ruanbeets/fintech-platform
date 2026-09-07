"""Bounded format detection and table extraction. No file is retained."""
import csv
import io
import json
import re
import subprocess
import sys
import zipfile
from itertools import islice
from datetime import date, datetime
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 5000
MAX_COLUMNS = 50
PDF_ERROR = "FinTrack cannot reliably read this scanned statement yet. Please export CSV/Excel or use a text-based PDF."
ALIASES = {
    "date": ["date", "transaction date", "posting date", "value date"],
    "description": ["description", "details", "reference", "merchant", "payee", "narrative"],
    "amount": ["amount", "value", "transaction amount"],
    "debit": ["debit", "money out", "withdrawal", "withdrawals", "spent"],
    "credit": ["credit", "money in", "deposit", "deposits", "received"],
    "balance": ["balance", "running balance"],
    "currency": ["currency", "ccy"], "category": ["category"],
    "transaction_type": ["type", "transaction type", "direction"],
}


def header_name(value):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(value).lower()).split())


def detect_mapping(headers):
    result = {}
    for field, aliases in ALIASES.items():
        hits = [i for i, name in enumerate(headers) if header_name(name) in aliases]
        result[field] = {"column": hits[0] if len(hits) == 1 else None,
                         "confidence": "high" if len(hits) == 1 else "ambiguous" if hits else "unmapped",
                         "candidates": hits}
    return result


def detect_header(rows):
    def score(row):
        mapping = detect_mapping(row)
        return sum(bool(v["candidates"]) for v in mapping.values()) + 2 * bool(mapping["date"]["candidates"])
    return max(range(min(50, len(rows))), key=lambda i: score(rows[i])) + 1 if rows else 1


def validate_tables(tables):
    count = 0
    if not tables or len(tables) > 10:
        raise ValueError("Use a file with 1–10 sheets/tables.")
    for name, rows in tables.items():
        if not rows:
            continue
        count += len(rows)
        if count > MAX_ROWS + 50 or any(len(r) > MAX_COLUMNS for r in rows):
            raise ValueError("File exceeds 5,000 rows or 50 columns. Split the export first.")
        for row in rows:
            for i, value in enumerate(row):
                if isinstance(value, (datetime, date)):
                    row[i] = value.isoformat()
                elif value is None:
                    row[i] = ""
                else:
                    row[i] = str(value)
                if len(row[i]) > 2000:
                    raise ValueError("A cell exceeds 2,000 characters; use a simpler export.")
    return tables


def parse_file(content, filename):
    if not content or len(content) > MAX_BYTES:
        raise ValueError("Choose a non-empty file no larger than 5 MB.")
    ext = Path(filename).suffix.lower()
    if ext not in {".csv", ".xlsx", ".xls", ".xlsb", ".ods", ".pdf"}:
        raise ValueError("Supported files: CSV, XLSX, XLS, XLSB, ODS and text-based PDF tables.")
    if ext == ".csv":
        if content.startswith((b"PK", b"%PDF", b"\xd0\xcf")) or b"\x00" in content[:200] and not content.startswith((b"\xff\xfe", b"\xfe\xff")):
            raise ValueError("The file contents do not match CSV.")
        try:
            text = content.decode("utf-16" if content.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
        except UnicodeError:
            text = content.decode("cp1252")
        try:
            dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
        except csv.Error:
            # Bank exports sometimes put title lines above the table, which defeats Sniffer.
            def header_score(delimiter):
                try:
                    sample = list(islice(csv.reader(io.StringIO(text), delimiter=delimiter, strict=True), 50))
                    return max((sum(bool(v["candidates"]) for v in detect_mapping(row).values()) for row in sample), default=0)
                except csv.Error:
                    return -1
            separator = max([",", ";", "\t", "|"], key=header_score)
            dialect = type("DetectedDialect", (csv.excel,), {"delimiter": separator})
        rows = []
        for row in csv.reader(io.StringIO(text), dialect, strict=True):
            rows.append(row)
            if len(rows) > MAX_ROWS + 50:
                raise ValueError("File exceeds 5,000 rows; split the export.")
        return "csv", validate_tables({"CSV": rows})
    if ext == ".pdf":
        if not content.startswith(b"%PDF"):
            raise ValueError("The file contents do not match PDF.")
        import pdfplumber
        tables = {}
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            if len(pdf.pages) > 20:
                raise ValueError("PDF limit: 20 pages.")
            for page in pdf.pages:
                if not (page.extract_text() or "").strip():
                    raise ValueError(PDF_ERROR)
                extracted = page.extract_tables()
                if not extracted:
                    raise ValueError("FinTrack could not find reliable transaction tables in this text-based PDF. Please export CSV/Excel.")
                for rows in extracted:
                    if not rows:
                        continue
                    mapping = detect_mapping(rows[0])
                    if not mapping["date"]["candidates"] or not (mapping["amount"]["candidates"] or mapping["debit"]["candidates"] or mapping["credit"]["candidates"]):
                        raise ValueError("PDF table structure is uncertain. Export CSV/Excel instead.")
                    key = json.dumps(rows[0])
                    tables.setdefault(key, [rows[0]]).extend(rows[1:])
        return "pdf", validate_tables({f"Table {i+1}": rows for i, rows in enumerate(tables.values())})
    if ext == ".xls":
        if not content.startswith(b"\xd0\xcf\x11\xe0"):
            raise ValueError("The file contents do not match XLS.")
    else:
        if not zipfile.is_zipfile(io.BytesIO(content)):
            raise ValueError("The spreadsheet is not a valid workbook.")
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            if sum(i.file_size for i in archive.infolist()) > 25 * 1024 * 1024 or len(archive.infolist()) > 2000:
                raise ValueError("Expanded workbook is too large.")
            names = set(archive.namelist())
            expected = {".xlsx": "xl/workbook.xml", ".xlsb": "xl/workbook.bin", ".ods": "content.xml"}[ext]
            if expected not in names:
                raise ValueError("The workbook contents do not match its extension.")
    from python_calamine import CalamineWorkbook
    with CalamineWorkbook.from_filelike(io.BytesIO(content)) as workbook:
        if len(workbook.sheet_names) > 10:
            raise ValueError("Workbook limit: 10 sheets.")
        tables = {}
        for name in workbook.sheet_names:
            sheet = workbook.get_sheet_by_name(name)
            if sheet.height > MAX_ROWS + 50 or sheet.width > MAX_COLUMNS:
                raise ValueError("Workbook exceeds the row/column limits.")
            tables[name] = sheet.to_python(skip_empty_area=False)
    return ext[1:], validate_tables(tables)


def parse_bounded(content, filename):
    # Isolate potentially expensive third-party parsers and terminate after 20 seconds.
    try:
        result = subprocess.run([sys.executable, "-m", "app.services.file_parser", Path(filename).suffix.lower()],
                                input=content, capture_output=True, timeout=20)
    except subprocess.TimeoutExpired:
        raise ValueError("File parsing exceeded 20 seconds. Please use a smaller CSV export.") from None
    try:
        output = json.loads(result.stdout)
    except (ValueError, UnicodeError):
        raise ValueError("Unable to reliably parse this file. Export a simpler CSV/Excel file.") from None
    if "error" in output:
        raise ValueError(output["error"])
    return output["format"], output["tables"]


if __name__ == "__main__":
    try:
        kind, tables = parse_file(sys.stdin.buffer.read(MAX_BYTES + 1), "upload" + sys.argv[1])
        print(json.dumps({"format": kind, "tables": tables}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
    except Exception:
        print(json.dumps({"error": "Unable to reliably parse this file. It may be encrypted, damaged or unsupported."}))
