from sqlalchemy.orm import Session
from uuid import UUID

from app.services.accounts_service import AccountsService
from app.services.analytics_service import AnalyticsService
from app.repositories.accounts_repository import AccountsRepository


class DashboardService:

    @staticmethod
    def get_dashboard_summary(db: Session, user_id: UUID):

        accounts = AccountsRepository.get_by_user(db, user_id)

        account_data = []
        total_balance = 0

        for account in accounts:

            balance = AccountsService.calculate_account_balance(db, account.id)

            account_data.append({
                "account_id": account.id,
                "account_name": account.name,
                "balance": balance
            })

            total_balance += balance

        cashflow = AnalyticsService.cashflow_summary(db, user_id)

        spending = AnalyticsService.spending_by_category(db, user_id)

        return {
            "summary": {
                "total_balance": total_balance,
                "monthly_income": cashflow["income"],
                "monthly_expenses": cashflow["expenses"],
                "savings_rate": (
                    (cashflow["income"] - cashflow["expenses"]) / cashflow["income"]
                    if cashflow["income"] else 0
                )
            },
            "accounts": account_data,
            "category_breakdown": spending
        }