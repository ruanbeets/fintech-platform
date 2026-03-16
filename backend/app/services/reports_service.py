from sqlalchemy.orm import Session
from uuid import UUID
from collections import defaultdict

from app.repositories.transactions_repository import TransactionsRepository


class ReportsService:

    @staticmethod
    def monthly_report(db: Session, user_id: UUID):

        transactions = TransactionsRepository.get_by_user(db, user_id)

        report = defaultdict(lambda: {"income": 0, "expenses": 0})

        for t in transactions:

            month = t.date.strftime("%Y-%m")

            if t.type == "income":
                report[month]["income"] += t.amount
            else:
                report[month]["expenses"] += t.amount

        return [
            {
                "month": month,
                "income": values["income"],
                "expenses": values["expenses"],
                "net": values["income"] - values["expenses"],
            }
            for month, values in sorted(report.items())
        ]


    @staticmethod
    def category_report(db: Session, user_id: UUID):

        transactions = TransactionsRepository.get_by_user(db, user_id)

        report = defaultdict(float)

        for t in transactions:

            if t.type != "expense":
                continue

            category = t.category.name if t.category else "Uncategorized"

            report[category] += t.amount

        return [
            {"category": category, "amount": amount}
            for category, amount in report.items()
        ]