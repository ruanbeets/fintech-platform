from collections import defaultdict
from datetime import datetime


def category_spending(transactions):

    result = defaultdict(float)

    for t in transactions:
        category = t.category.name if t.category else "Uncategorized"

        if t.type == "expense":
            result[category] += t.amount

    return [
        {"category": category, "amount": amount}
        for category, amount in result.items()
    ]


def monthly_spending(transactions):

    monthly = defaultdict(float)

    for t in transactions:

        if t.type != "expense":
            continue

        month = t.date.strftime("%Y-%m")

        monthly[month] += t.amount

    return [
        {"month": month, "total": total}
        for month, total in sorted(monthly.items())
    ]