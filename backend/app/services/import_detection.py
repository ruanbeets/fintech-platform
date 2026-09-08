"""Small, inspectable locale suggestions. Ambiguous dates still require review."""
import re
from app.schemas.imports import Mapping
from app.services.import_normalization import amount_model


def suggestions(rows, header, mapping):
    fields = Mapping(**{k: v["column"] for k, v in mapping.items()})
    model = amount_model(rows[header-1], fields, rows=rows[header:])
    date_votes, number_votes = set(), set()
    for row in rows[header:]:
        if fields.date is not None and fields.date < len(row):
            raw = str(row[fields.date]).strip()
            if re.match(r"^\d{4}[-/]", raw):
                date_votes.add("YMD")
            elif match := re.match(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-]\d{4}$", raw):
                a, b = map(int, match.groups())
                if a > 12:
                    date_votes.add("DMY")
                if b > 12:
                    date_votes.add("MDY")
        for index in [fields.amount, fields.debit, fields.credit, fields.fee, fields.balance]:
            raw = str(row[index]).strip() if index is not None and index < len(row) else ""
            if re.search(r",\d{1,2}\)?$", raw):
                number_votes.add("comma")
            if re.search(r"\.\d{1,2}\)?$", raw):
                number_votes.add("dot")
    defaults = {"amount_model": model, "date_order": next(iter(date_votes)) if len(date_votes) == 1 else "DMY",
                "number_format": next(iter(number_votes)) if len(number_votes) == 1 else "dot",
                "sign_convention": "negative_expense"}
    high = fields.date is not None and fields.description is not None and any(i is not None for i in (fields.amount, fields.debit, fields.credit, fields.fee))
    high = high and not any(v["confidence"] == "ambiguous" for v in mapping.values()) and len(date_votes) == 1 and len(number_votes) <= 1
    return defaults, bool(high)
