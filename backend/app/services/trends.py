"""Behaviour trends derived from the shared, already-scoped monthly ledger."""
from collections import defaultdict
from datetime import date
from decimal import Decimal

from app.schemas.trends import FinancialTrends
from app.services.financial_analytics import ZERO, money, month_start, shift_month, rate
from app.services.recurring import METHODOLOGY, category_name, detect_recurring, group_key


def comparison(current, baseline, coverage):
    delta = current - baseline if baseline is not None else None
    return {"baseline": baseline, "absolute_change": money(delta) if delta is not None else None,
            "percentage_change": money(delta / baseline * 100) if baseline else None, "coverage": coverage}


def calculate_trends(rows, history, *, earliest, cutoff, previous_valid):
    """Use the existing monthly income/expense/net/rate outputs, never recalculate them."""
    selected, previous = history[-1], history[-2]
    selected_date = date.fromisoformat(selected["month"] + "-01")
    scoped = [(tx, occurred, amount) for tx, occurred, amount in rows if occurred <= cutoff]
    sums = defaultdict(lambda: defaultdict(lambda: ZERO))
    for tx, occurred, amount in scoped:
        if tx.type == "expense":
            sums[category_name(tx)][month_start(occurred).isoformat()[:7]] += amount
    categories = []
    for category, monthly in sums.items():
        if not any(monthly.get(m["month"], ZERO) for m in history):
            continue
        current, prior = monthly.get(selected["month"], ZERO), monthly.get(previous["month"], ZERO)
        def average(count):
            if earliest is None or shift_month(selected_date, 1 - count) < earliest:
                return None
            return money(sum((monthly.get(m["month"], ZERO) for m in history[-count:]), ZERO) / count)
        categories.append(dict(category=category, current_spend=money(current), previous_spend=money(prior),
                               change=comparison(current, prior, previous["coverage"]),
                               trailing_3_month_average=average(3), trailing_6_month_average=average(6),
                               share_of_expenses=money(current / selected["expenses"] * 100) if selected["expenses"] else None,
                               history=[dict(month=m["month"], spend=money(monthly.get(m["month"], ZERO)),
                                             coverage=m["coverage"], partial_month=m["partial_month"]) for m in history]))
    categories.sort(key=lambda c: (-c["current_spend"], c["category"]))
    eligible = [m for m in history if m["transaction_count"] and not m["partial_month"]]
    def extreme(fn):
        if not eligible:
            return None
        m = fn(eligible, key=lambda m: m["income"])
        return {"month": m["month"], "income": m["income"]}
    avg12 = (money(sum((m["income"] for m in history), ZERO) / 12)
             if earliest is not None and earliest <= date.fromisoformat(history[0]["month"] + "-01") else None)
    income = dict(current=selected["income"], previous_month=comparison(selected["income"], previous["income"], previous["coverage"]),
                  versus_3_month_average=comparison(selected["income"], selected["trailing_3_month"].get("income"), selected["trailing_3_month"]["status"]),
                  versus_6_month_average=comparison(selected["income"], selected["trailing_6_month"].get("income"), selected["trailing_6_month"]["status"]),
                  average_12_month=avg12, recorded_months=sum(bool(m["transaction_count"]) for m in history),
                  highest_month=extreme(max), lowest_month=extreme(min),
                  coverage_note="Averages include the selected month and missing calendar months as zero recorded income. High/low exclude missing and partial months; among recorded complete calendar months only. Record completeness is not independently verified. Earliest month wins ties.")

    def rate_month(m):
        return {"month": m["month"], "savings_rate": m["savings_rate"], "coverage": m["coverage"], "partial_month": m["partial_month"]}
    def rate_average(count):
        # Arithmetic mean of available monthly rates; use unrounded ratios until final display rounding.
        values = [rate(m["income"], m["net_cash_flow"], rounded=False) for m in history[-count:] if m["income"]]
        return {"value": money(sum(values, ZERO) / len(values)) if values else None,
                "valid_months": len(values), "window_months": count}
    savings = dict(current=selected["savings_rate"], previous_valid=rate_month(previous_valid) if previous_valid else None,
                   change_percentage_points=money(selected["savings_rate"] - previous_valid["savings_rate"])
                       if selected["savings_rate"] is not None and previous_valid else None,
                   trailing_3_month_average=rate_average(3), trailing_6_month_average=rate_average(6),
                   history=[rate_month(m) for m in history],
                   methodology="Arithmetic mean of valid monthly savings rates, using unrounded ratios. Zero-income/unavailable months are excluded, never replaced by zero. Includes the selected month, including partial activity when labeled. This differs from Overview's income-weighted aggregate rate. Percentage-point change compares displayed monthly rates to the previous valid recorded month.")
    recurring, accepted = detect_recurring(scoped, cutoff=cutoff)
    variable_categories = {"Groceries", "Food", "Dining", "Transport", "Health", "Shopping", "Travel", "Entertainment", "Maintenance"}
    buckets = {key: {"amount": ZERO, "transaction_count": 0} for key in ["fixed_recurring", "variable", "unclassified"]}
    for tx, occurred, amount in scoped:
        if tx.type != "expense" or month_start(occurred) != selected_date:
            continue
        category, key = category_name(tx), group_key(tx)
        match = accepted.get(key)
        if category in variable_categories:
            classification = "variable"
        elif match and abs(amount - match[0]) <= match[1]:
            classification = "fixed_recurring"
        elif category in {"Uncategorised", "Other", "Unknown"}:
            classification = "unclassified"
        else:
            classification = "variable"
        buckets[classification]["amount"] += amount
        buckets[classification]["transaction_count"] += 1
    explanations = {
        "fixed_recurring": "Observed expenses matching a recurring candidate and amount tolerance, excluding variable-behaviour categories. Likely repeat costs, not confirmed fixed commitments.",
        "variable": "Groceries, food, dining, transport, health, shopping, travel, entertainment and maintenance; plus other categorized expenses without matching recurring evidence.",
        "unclassified": "Uncategorised/Other/Unknown expenses without sufficient recurring evidence."
    }
    spending = dict(total_expenses=selected["expenses"], classes=[dict(classification=key, amount=money(b["amount"]),
                    share=money(b["amount"] / selected["expenses"] * 100) if selected["expenses"] else None,
                    transaction_count=b["transaction_count"], explanation=explanations[key]) for key, b in buckets.items()],
                    methodology="Rule-based estimates partition the selected month's recorded expenses, not a prediction of a typical future month. Fixed/recurring + variable + unclassified reconcile to expenses. Transfers and income are excluded. Missing records cannot establish actual commitments; rounded shares may not sum to exactly 100%.")
    return FinancialTrends(categories=categories, income=income, savings=savings, recurring=recurring,
                           spending=spending, recurring_methodology=METHODOLOGY, observed_through=cutoff.isoformat())
