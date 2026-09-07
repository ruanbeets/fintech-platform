"""Explicit locale/sign choices; invalid financial cells never become zero."""
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from app.schemas.imports import NormalizedRow, RowResult

CURRENCIES = {"ZAR", "USD", "EUR", "GBP", "AUD", "CAD", "NZD", "CHF", "JPY", "INR", "BWP", "NAD", "KES", "NGN", "SGD", "HKD"}
SYMBOLS = {"R": "ZAR", "€": "EUR", "£": "GBP"}  # $ is ambiguous; selected currency is explicit.
TYPE_NAMES = {"income": "income", "credit": "income", "deposit": "income", "in": "income",
              "expense": "expense", "debit": "expense", "withdrawal": "expense", "out": "expense",
              "transfer": "transfer", "internal transfer": "transfer"}


def decimal_value(value, number_format, currency, optional=False):
    text = str(value if value is not None else "").strip().replace("\u00a0", " ")
    if not text:
        if optional:
            return None
        raise ValueError("Amount is blank.")
    if text.startswith("="):
        raise ValueError("Formula cells cannot be imported as amounts.")
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1].strip()
    sign = ""
    if text.startswith(("-", "+")):
        sign, text = text[0], text[1:].strip()
    for symbol, code in SYMBOLS.items():
        if (re.search(r"(?<![A-Za-z])R(?![A-Za-z])", text) if symbol == "R" else symbol in text) and currency != code:
            raise ValueError("Currency symbol conflicts with the selected currency.")
    codes = [code for code in re.findall(r"(?<![A-Za-z])[A-Za-z]{3}(?![A-Za-z])", text) if code.upper() in CURRENCIES]
    if any(code.upper() != currency for code in codes):
        raise ValueError("Amount currency conflicts with the selected currency.")
    text = re.sub(r"(?<![A-Za-z])(?:" + "|".join(sorted(CURRENCIES)) + r")(?![A-Za-z])", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^[R$€£]\s*", "", text)
    decimal_sep, group_sep = (".", ",") if number_format == "dot" else (",", ".")
    # Spaces are accepted only as proper thousands groups.
    if text.startswith(("-", "+")):
        if sign or negative:
            raise ValueError("Amount has conflicting sign markers.")
        sign, text = text[0], text[1:]
    integer, sep, fraction = text.partition(decimal_sep)
    if sep and (not fraction.isdigit() or len(fraction) > 2):
        raise ValueError("Amount must have at most two decimal places; verify decimal separator.")
    if group_sep in integer or " " in integer:
        if group_sep in integer and " " in integer:
            raise ValueError("Mixed thousands separators.")
        separator = group_sep if group_sep in integer else " "
        if not re.fullmatch(r"\d{1,3}(?:" + re.escape(separator) + r"\d{3})+", integer):
            raise ValueError("Invalid thousands grouping; verify number format.")
        integer = integer.replace(separator, "")
    if not integer.isdigit():
        raise ValueError("Amount is not a valid number.")
    try:
        amount = Decimal(("-" if negative else sign) + integer + ("." + fraction if sep else ""))
    except InvalidOperation:
        raise ValueError("Invalid amount.") from None
    if not amount.is_finite() or abs(amount) >= Decimal("1000000000000"):
        raise ValueError("Amount is outside the supported range.")
    return amount.quantize(Decimal("0.01"))


def normalized_date(value, order):
    text = str(value).strip()
    try:
        value = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if value.tzinfo:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
    except ValueError:
        if re.fullmatch(r"\d{5}(?:\.0+)?", text):
            value = datetime(1899, 12, 30) + timedelta(days=int(Decimal(text)))
        else:
            formats = {"DMY": ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %b %Y", "%d %B %Y"],
                       "MDY": ["%m/%d/%Y", "%m-%d-%Y", "%b %d %Y"],
                       "YMD": ["%Y/%m/%d", "%Y-%m-%d"]}[order]
            value = None
            for fmt in formats:
                try:
                    value = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    pass
            if value is None:
                raise ValueError("Invalid date for the selected date order.") from None
    if not 1900 <= value.year <= 2100:
        raise ValueError("Date is outside 1900–2100.")
    if value.date() > datetime.now(timezone.utc).date():
        raise ValueError("Future-dated transaction; review the date before importing.")
    return value


def fingerprint(row):
    parts = [row.account.strip().casefold(), row.date.isoformat(), " ".join(row.description.casefold().split()),
             str(row.amount), row.currency, row.transaction_type]
    return hashlib.sha256(json.dumps(parts, ensure_ascii=True).encode()).hexdigest()


def normalize_rows(rows, options, batch_id, source_file, existing):
    if len(rows) - options.header_row > 5000:
        raise ValueError("Import limit: 5,000 rows per table. Split the export first.")
    mapping = options.mapping.model_dump()
    used = [v for v in mapping.values() if v is not None]
    if len(used) != len(set(used)) or any(v < 0 or v >= len(rows[options.header_row-1]) for v in used):
        raise ValueError("Each mapped field needs a different valid column.")
    if mapping["date"] is None or mapping["description"] is None:
        raise ValueError("Map a date column and description/reference column.")
    if mapping["amount"] is None and mapping["debit"] is None and mapping["credit"] is None:
        raise ValueError("Map Amount or Debit/Credit columns.")
    if mapping["amount"] is not None and (mapping["debit"] is not None or mapping["credit"] is not None):
        raise ValueError("Use Amount OR Debit/Credit, not both.")
    if options.currency not in CURRENCIES:
        raise ValueError("Unsupported currency code. Choose a supported three-letter currency.")
    if not options.account.strip():
        raise ValueError("Provide an account label (not an account number).")
    seen, results = set(existing), []
    for number, source in enumerate(rows[options.header_row:], options.header_row + 1):
        if not any(str(c).strip() for c in source):
            continue
        if number in options.excluded_rows:
            results.append(RowResult(source_row=number, status="excluded"))
            continue
        def cell(field):
            index = mapping[field]
            return str(source[index]).strip() if index is not None and index < len(source) else ""
        try:
            description = " ".join(cell("description").split())
            if not description or len(description) > 500:
                raise ValueError("Description is blank or exceeds 500 characters.")
            currency = cell("currency").upper() or options.currency
            if currency != options.currency:
                raise ValueError("Row currency differs from selected currency; import this currency separately.")
            if mapping["amount"] is not None:
                signed = decimal_value(cell("amount"), options.number_format, currency)
                kind = "expense" if (signed < 0) == (options.sign_convention == "negative_expense") else "income"
                amount = abs(signed)
            else:
                debit = decimal_value(cell("debit"), options.number_format, currency, optional=True) or Decimal("0")
                credit = decimal_value(cell("credit"), options.number_format, currency, optional=True) or Decimal("0")
                if debit < 0 or credit < 0 or (debit and credit) or (not debit and not credit):
                    raise ValueError("Debit/Credit requires one positive value and a blank/zero opposite value.")
                kind, amount = ("expense", debit) if debit else ("income", credit)
            source_type = cell("transaction_type").casefold()
            if source_type and number not in options.type_overrides:
                if source_type not in TYPE_NAMES:
                    raise ValueError("Unrecognized transaction type; use a row override or fix the mapping.")
                kind = TYPE_NAMES[source_type]
            kind = options.type_overrides.get(number, kind)
            if not amount:
                raise ValueError("Zero-value transaction; exclude or correct it.")
            row = NormalizedRow(source_row=number, date=normalized_date(cell("date"), options.date_order),
                                description=description, amount=amount, transaction_type=kind,
                                category=cell("category") or None, currency=currency, account=options.account.strip(),
                                balance_optional=decimal_value(cell("balance"), options.number_format, currency, optional=True),
                                source_file=source_file, import_batch_id=batch_id)
            key = fingerprint(row)
            status = "duplicate" if key in seen else "valid"
            seen.add(key)
            results.append(RowResult(source_row=number, status=status, transaction=row))
        except ValueError as exc:
            results.append(RowResult(source_row=number, status="invalid", errors=[str(exc)]))
    return results
