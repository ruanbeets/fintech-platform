from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.budgets_repository import BudgetsRepository
from app.repositories.transactions_repository import TransactionsRepository
from app.domain.events.budget_exceeded import check_budget_exceeded


class BudgetsService:

    @staticmethod
    def create_budget(db: Session, user_id: UUID, category_id: UUID, limit: float):

        return BudgetsRepository.create(
            db=db,
            user_id=user_id,
            category_id=category_id,
            limit=limit,
        )


    @staticmethod
    def get_user_budgets(db: Session, user_id: UUID):

        return BudgetsRepository.get_by_user(db, user_id)


    @staticmethod
    def check_budget_status(db: Session, user_id: UUID):

        budgets = BudgetsRepository.get_by_user(db, user_id)

        transactions = TransactionsRepository.get_by_user(db, user_id)

        alerts = []

        for budget in budgets:

            spent = 0

            for t in transactions:

                if t.category_id == budget.category_id and t.type == "expense":
                    spent += t.amount

            event = check_budget_exceeded(spent, budget.limit)

            if event:
                alerts.append({
                    "category_id": budget.category_id,
                    "spent": spent,
                    "limit": budget.limit
                })

        return alerts