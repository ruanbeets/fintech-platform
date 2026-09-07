"""Pure deterministic analytics, independent of database sessions and UI."""
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from app.schemas.dashboard import DashboardSummary

ZERO = Decimal("0.00")
BALANCE_REASON = "No opening balance, balance snapshot, or valuation is recorded. Transaction net flows are not account balances."


def month_start(value):
    return date(value.year, value.month, 1)


def shift_month(value, offset):
    index = value.year * 12 + value.month - 1 + offset
    year, month = divmod(index, 12)
    return date(year, month + 1, 1)


def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def rate(income, net, *, rounded=True):
    if not income:
        return None
    value = net / income * 100
    return money(value) if rounded else value


def utc_date(value):
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.astimezone(timezone.utc).date()
    return value.date() if isinstance(value, datetime) else value


def calculate_overview(accounts, transactions, *, user_id, as_of, selected_month=None, currency=None, demo=False):
    """Missing months mean zero recorded activity, never verified coverage.

    Rolling windows include the displayed month. No floats enter calculations.
    """
    owned = {str(a.id): a for a in accounts if str(a.user_id) == str(user_id)}
    currencies = sorted({a.currency.upper() for a in owned.values()})
    currency = (currency or (currencies[0] if currencies else "ZAR")).upper()
    if currencies and currency not in currencies:
        raise ValueError("Currency is not present in this user's accounts")
    valid = []
    for tx in transactions:
        account = owned.get(str(tx.account_id))
        if str(tx.user_id) != str(user_id) or account is None or account.currency.upper() != currency:
            continue
        occurred = utc_date(tx.occurred_at)
        if occurred > as_of:
            continue
        amount = Decimal(str(tx.amount))
        if not amount.is_finite() or amount <= 0 or tx.type not in {"income", "expense", "transfer"}:
            raise ValueError("Invalid recorded transaction; correct its amount or type before calculating analytics")
        valid.append((tx, occurred, amount))
    current = month_start(as_of)
    latest = max((month_start(d) for _, d, _ in valid), default=current)
    selected = date.fromisoformat(selected_month + "-01") if selected_month else latest
    if selected > current or selected.year < 3:
        raise ValueError("Select a historical month from year 0003 onward")
    earliest = min((month_start(d) for _, d, _ in valid), default=None)
    buckets = {}
    lifetime_income, lifetime_expenses = ZERO, ZERO
    for tx, occurred, amount in valid:
        bucket = buckets.setdefault(month_start(occurred), {"income": ZERO, "expenses": ZERO, "count": 0})
        bucket["count"] += 1
        if tx.type == "income":
            bucket["income"] += amount
            lifetime_income += amount
        elif tx.type == "expense":
            bucket["expenses"] += amount
            lifetime_expenses += amount

    def bucket_for(month):
        return buckets.get(month, {"income": ZERO, "expenses": ZERO, "count": 0})

    def rolling(month, count):
        start = shift_month(month, 1 - count)
        window = [bucket_for(shift_month(start, i)) for i in range(count)]
        recorded = sum(b["count"] > 0 for b in window)
        result = {"months": count, "recorded_months": recorded, "status": "insufficient_history"}
        if earliest is None or start < earliest:
            return result
        income = sum((b["income"] for b in window), ZERO)
        expenses = sum((b["expenses"] for b in window), ZERO)
        result.update(income=money(income / count), expenses=money(expenses / count),
                      net_cash_flow=money((income - expenses) / count), savings_rate=rate(income, income - expenses),
                      status="partial_month" if month == current else "recorded_activity")
        return result

    def monthly(month):
        b = bucket_for(month)
        net = b["income"] - b["expenses"]
        return {"month": month.strftime("%Y-%m"), "income": money(b["income"]), "expenses": money(b["expenses"]),
                "net_cash_flow": money(net), "savings_rate": rate(b["income"], net), "transaction_count": b["count"],
                "coverage": "recorded_activity" if b["count"] else "no_recorded_activity", "partial_month": month == current,
                "trailing_3_month": rolling(month, 3), "trailing_6_month": rolling(month, 6)}

    first = min(earliest or shift_month(current, -11), selected, shift_month(current, -11))
    count = (current.year - first.year) * 12 + current.month - first.month + 1
    from app.services.trends import calculate_trends
    history = [monthly(shift_month(selected, i)) for i in range(-11, 1)]
    prior_income_months = [m for m, b in buckets.items() if m < selected and b["income"]]
    previous_valid = monthly(max(prior_income_months)) if prior_income_months else None
    cutoff = min(as_of, shift_month(selected, 1) - timedelta(days=1))
    return DashboardSummary(
        trends=calculate_trends(valid, history, earliest=earliest, cutoff=cutoff, previous_valid=previous_valid),
        currency=currency, available_currencies=currencies, selected_month=selected.strftime("%Y-%m"),
        available_months=[shift_month(first, i).strftime("%Y-%m") for i in reversed(range(count))],
        as_of=as_of.isoformat(), demo=demo, selected=monthly(selected),
        history=history,
        account_balances=[{"account_id": str(a.id), "name": a.name, "currency": currency, "reason": BALANCE_REASON}
                          for a in owned.values() if a.currency.upper() == currency],
        net_worth={"reason": "Asset valuations and liability balances are not recorded; net worth cannot be supported."},
        coverage_note="Recorded transactions only. Missing months mean zero recorded activity, not confirmed zero spending. Rolling averages include the displayed month and all calendar months in the window. Savings rates use total income and net cash flow, not an average of percentages. Dates use UTC; the current month is partial.",
        income=money(lifetime_income), expense=money(lifetime_expenses), net=money(lifetime_income - lifetime_expenses))
