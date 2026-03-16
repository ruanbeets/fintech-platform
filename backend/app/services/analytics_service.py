from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.transactions_repository import TransactionsRepository
from app.domain.analytics.spending import category_spending, monthly_spending
from app.domain.analytics.cashflow import calculate_cashflow
from app.domain.analytics.forecasting import forecast_balance
from app.repositories.accounts_repository import AccountsRepository
from app.services.accounts_service import AccountsService


class AnalyticsService:

    @staticmethod
    def spending_by_category(db: Session, user_id: UUID):

        transactions = TransactionsRepository.get_by_user(db, user_id)

        return category_spending(transactions)


    @staticmethod
    def monthly_spending(db: Session, user_id: UUID):

        transactions = TransactionsRepository.get_by_user(db, user_id)

        return monthly_spending(transactions)


    @staticmethod
    def cashflow_summary(db: Session, user_id: UUID):

        transactions = TransactionsRepository.get_by_user(db, user_id)

        return calculate_cashflow(transactions)


    @staticmethod
    def balance_forecast(db: Session, user_id: UUID, months: int = 6):

        accounts = AccountsRepository.get_by_user(db, user_id)

        current_balance = 0

        for account in accounts:
            current_balance += AccountsService.calculate_account_balance(db, account.id)

        cashflow = AnalyticsService.cashflow_summary(db, user_id)

        monthly_net = cashflow["net"]

        return forecast_balance(current_balance, monthly_net, months)