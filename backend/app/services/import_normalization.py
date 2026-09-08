"""Explicit locale/sign choices; invalid financial cells never become zero."""
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from app.schemas.imports import NormalizedRow, RowResult
from app.services.file_parser import header_name

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
        if negative:
            raise ValueError("Amount has conflicting sign markers.")
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
            for fmt in [f + suffix for f in formats for suffix in ("", " %H:%M", " %H:%M:%S")]:
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
    if row.signed_amount is not None:
        # Classification is reviewable and must not change transaction identity.
        parts = parts[:-1] + [str(row.signed_amount), str(row.balance_optional), row.source_reference, row.occurrence]
    return hashlib.sha256(json.dumps(parts, ensure_ascii=True).encode()).hexdigest()


def amount_model(headers, mapping, requested="auto", rows=None):
    if requested != "auto":
        return requested
    if mapping.amount is not None:
        return "signed"
    names = [header_name(headers[i]) for i in [mapping.debit, mapping.credit] if i is not None and i < len(headers)]
    if any(n in {"money in", "money out"} for n in names):
        # Money Out is exported either as signed values or positive magnitudes.
        # Both are supported; mixed conventions remain row-level errors.
        values = [str(r[i]).strip() for r in (rows or []) for i in (mapping.debit, mapping.fee) if i is not None and i < len(r) and str(r[i]).strip()]
        if values and not any("-" in v or "(" in v for v in values):
            return "debit_credit"
        return "money_columns"
    return "debit_credit"


def movement(cell, mapping, options, model, currency):
    fee = decimal_value(cell("fee"), options.number_format, currency, optional=True)
    if mapping["amount"] is not None:
        if model != "signed":
            raise ValueError("Select the Signed amount model for an Amount column.")
        signed = decimal_value(cell("amount"), options.number_format, currency)
        if options.sign_convention == "positive_expense":
            signed = -signed
        # The single Amount is the total movement. Fee is provenance, never added again.
    else:
        if model == "signed":
            raise ValueError("Map an Amount column for the Signed amount model.")
        debit = decimal_value(cell("debit"), options.number_format, currency, optional=True) or Decimal("0")
        credit = decimal_value(cell("credit"), options.number_format, currency, optional=True) or Decimal("0")
        if debit and credit:
            raise ValueError("Row has both debit and credit values; review the source.")
        if model == "money_columns":
            if credit < 0 or debit > 0 or (fee is not None and fee > 0):
                raise ValueError("Money In must be positive; Money Out and Fee negative. Check the amount model.")
            signed = credit + debit + (fee or Decimal("0"))
        else:
            if credit < 0 or debit < 0 or (fee is not None and fee < 0):
                raise ValueError("Debit/Credit uses positive magnitudes. Choose Money In/Out for signed columns.")
            signed = credit - debit - (fee or Decimal("0"))
    if not signed:
        raise ValueError("Row has no non-zero financial movement (no amount).")
    if abs(signed) >= Decimal("1000000000000"):
        raise ValueError("Combined movement is outside the supported range.")
    return signed, abs(fee) if fee is not None else None


def apply_duplicates(results, existing):
    seen = set(existing)
    for result in results:
        if result.status != "valid":
            continue
        key = fingerprint(result.transaction)
        if key in seen:
            result.status = "duplicate"
        seen.add(key)
    return results


def normalize_rows(rows, options, batch_id, source_file, existing, check_duplicates=True):
    if len(rows) - options.header_row > 5000:
        raise ValueError("Import limit: 5,000 rows per table. Split the export first.")
    mapping = options.mapping.model_dump()
    used = [v for v in mapping.values() if v is not None]
    if len(used) != len(set(used)) or any(v < 0 or v >= len(rows[options.header_row-1]) for v in used):
        raise ValueError("Each mapped field needs a different valid column.")
    if mapping["date"] is None or mapping["description"] is None:
        raise ValueError("Map a date column and description/reference column.")
    if all(mapping[k] is None for k in ("amount", "debit", "credit", "fee")):
        raise ValueError("Map Amount or Debit/Credit columns.")
    if mapping["amount"] is not None and (mapping["debit"] is not None or mapping["credit"] is not None):
        raise ValueError("Use Amount OR Debit/Credit, not both.")
    if options.currency not in CURRENCIES:
        raise ValueError("Unsupported currency code. Choose a supported three-letter currency.")
    if not options.account.strip():
        raise ValueError("Provide an account label (not an account number).")
    results, occurrences = [], {}
    model = amount_model(rows[options.header_row-1], options.mapping, options.amount_model, rows[options.header_row:])
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
            if not cell("date") and not any(cell(k) for k in ("amount", "debit", "credit", "fee")):
                results.append(RowResult(source_row=number, status="excluded", errors=["Metadata without a date or movement."]))
                continue
            if source == rows[options.header_row-1] or header_name(description) in {
                "opening balance", "closing balance", "balance brought forward", "balance carried forward",
                "statement total", "statement totals", "total", "totals"}:
                results.append(RowResult(source_row=number, status="excluded", errors=["Statement header/summary; not a transaction."]))
                continue
            if not description or len(description) > 500:
                raise ValueError("Description is blank or exceeds 500 characters.")
            currency = cell("currency").upper() or options.currency
            if currency != options.currency:
                raise ValueError("Row currency differs from selected currency; import this currency separately.")
            signed, fee = movement(cell, mapping, options, model, currency)
            kind, amount = ("expense" if signed < 0 else "income"), abs(signed)
            transfer_names = {"transfer", "transfers", "internal transfer", "internal transfers", "transfer in", "transfer out"}
            if any(header_name(cell(k)) in transfer_names for k in ("category", "parent_category")):
                kind = "transfer"
            source_type = cell("transaction_type").casefold()
            if source_type and number not in options.type_overrides:
                if source_type not in TYPE_NAMES:
                    raise ValueError("Unrecognized transaction type; use a row override or fix the mapping.")
                if kind != "transfer" or source_type not in {"credit", "deposit", "in", "debit", "withdrawal", "out"}:
                    kind = TYPE_NAMES[source_type]
            kind = options.type_overrides.get(number, kind)
            if not amount:
                raise ValueError("Zero-value transaction; exclude or correct it.")
            booking = normalized_date(cell("date"), options.date_order)
            # Never expose the source account number in previews or analytics labels.
            reference = cell("account")
            account = ("Imported account " + hashlib.sha256(reference.encode()).hexdigest()[:20]) if reference else options.account.strip()
            row = NormalizedRow(source_row=number, date=booking, booking_date=booking,
                                description=description, amount=amount, transaction_type=kind,
                                category=cell("category") or ("Bank fees" if fee and amount == fee else None), currency=currency, account=account,
                                balance_optional=decimal_value(cell("balance"), options.number_format, currency, optional=True),
                                source_file=source_file, import_batch_id=batch_id,
                                transaction_datetime=normalized_date(cell("transaction_datetime"), options.date_order) if cell("transaction_datetime") else None,
                                original_description=cell("original_description") or None,
                                signed_amount=signed, direction="CREDIT" if signed > 0 else "DEBIT", fee_amount=fee,
                                source_parent_category=cell("parent_category") or None, source_category=cell("category") or None,
                                source_reference=hashlib.sha256(cell("source_reference").encode()).hexdigest() if cell("source_reference") else None)
            # Repeated no-balance purchases are retained. Across uploads, occurrence
            # matching is only a possible duplicate and is explicitly shown in review.
            base = fingerprint(row)
            if row.balance_optional is None and row.source_reference is None:
                occurrences[base] = occurrences.get(base, 0) + 1
                row.occurrence = occurrences[base]
            results.append(RowResult(source_row=number, status="valid", transaction=row))
        except ValueError as exc:
            results.append(RowResult(source_row=number, status="invalid", errors=[str(exc)]))
    return apply_duplicates(results, existing) if check_duplicates else results
