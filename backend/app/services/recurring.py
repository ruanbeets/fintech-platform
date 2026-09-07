"""Conservative rules for likely recurrence, with no future cash-flow projection."""
import calendar
import re
import unicodedata
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from statistics import median

from app.services.financial_analytics import money, month_start, shift_month

METHODOLOGY = (
    "Lookback: 12 calendar months through the selected period; no later transactions are used. "
    "Group by account, type, category and normalized merchant (description fallback). "
    "Normalize case, accents, punctuation, dated references and common payment prefixes; no fuzzy merchant merging. "
    "At least 3 monthly or 4 weekly/fortnightly occurrences are required. At least 80% of amounts must be "
    "within 10% (minimum R1 or one currency unit) of the median; at least 80% of intervals must match. "
    "Monthly intervals allow ±5 days and one skipped month per interval; weekly/fortnightly allow ±2 days. "
    "Strong means at least 6 occurrences and at least 90% amount/interval agreement. These are candidates, not confirmed commitments."
)


def normalize_name(value):
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    value = re.sub(r"\b\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?\b", " ", value)
    value = re.sub(r"\b(?:ref(?:erence)?|txn)\s*[:#-]?\s*[a-z0-9-]+", " ", value)
    value = re.sub(r"^(?:synthetic demo\s*:|debit order\s*:|card purchase\s*:|payment to\s+)", "", value)
    value = re.sub(r"\b\d{6,}\b", " ", value)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def category_name(tx):
    return " ".join((getattr(tx, "category", None) or "").split()).title() or "Uncategorised"


def group_key(tx):
    name = normalize_name(getattr(tx, "merchant", None) or getattr(tx, "description", None))
    return str(tx.account_id), tx.type, category_name(tx), name


def monthly_date(value, count, anchor_day=None):
    month = shift_month(month_start(value), count)
    return month.replace(day=min(anchor_day or value.day, calendar.monthrange(month.year, month.month)[1]))


def detect_recurring(rows, *, cutoff):
    """Rows have already passed the shared user/currency/amount validation.

    Returns public candidate evidence plus internal keys for observed-expense classification.
    """
    first_month = shift_month(month_start(cutoff), -11)
    groups = defaultdict(list)
    for tx, occurred, amount in rows:
        key = group_key(tx)
        if first_month <= occurred <= cutoff and key[-1]:
            groups[key].append((occurred, amount))
    candidates, accepted = [], {}
    for key, entries in sorted(groups.items()):
        entries.sort()
        if len(entries) < 3:
            continue
        dates = [d for d, _ in entries]
        typical = median([amount for _, amount in entries])
        tolerance = max(Decimal("1"), typical * Decimal("0.10"))
        amount_hits = sum(abs(amount - typical) <= tolerance for _, amount in entries)
        if amount_hits * 5 < len(entries) * 4:
            continue
        best = None
        for frequency, days in [("monthly", None), ("weekly", 7), ("fortnightly", 14)]:
            if days and len(entries) < 4:
                continue
            if frequency == "monthly" and len({month_start(d) for d in dates}) != len(dates):
                continue
            hits, direct_hits = 0, 0
            for previous, current in zip(dates, dates[1:]):
                if frequency == "monthly":
                    distance = (current.year - previous.year) * 12 + current.month - previous.month
                    match = distance in {1, 2} and abs((current - monthly_date(previous, distance)).days) <= 5
                    direct_hits += match and distance == 1
                else:
                    match = abs((current - previous).days - days) <= 2
                    direct_hits += match
                hits += match
            if hits * 5 >= (len(entries) - 1) * 4 and direct_hits >= 2:
                best = frequency, days, hits
                break
        if best is None:
            continue
        frequency, days, interval_hits = best
        strong = len(entries) >= 6 and amount_hits * 10 >= len(entries) * 9 and interval_hits * 10 >= (len(entries) - 1) * 9
        proposed = (monthly_date(dates[-1], 1, int(median([d.day for d in dates])))
                    if frequency == "monthly" else dates[-1] + timedelta(days=days))
        next_date = proposed.isoformat() if strong and proposed > cutoff else None
        candidates.append(dict(
            normalized_name=key[-1], account_id=key[0], transaction_type=key[1], category=key[2],
            typical_amount=money(typical), frequency=frequency, strength="strong" if strong else "likely",
            first_observed=dates[0].isoformat(), most_recent=dates[-1].isoformat(), occurrence_count=len(entries),
            expected_next_occurrence=next_date,
            next_occurrence_note="Approximate cadence date, not a scheduled payment." if next_date else
                "Unavailable: evidence is not strong enough or the next cadence date already passed; no date is rolled forward.",
            evidence=f"{amount_hits}/{len(entries)} amounts within 10% (minimum 1 currency unit) of the median; "
                     f"{interval_hits}/{len(entries)-1} intervals match {frequency} cadence."
        ))
        accepted[key] = (typical, tolerance)
    return candidates, accepted
