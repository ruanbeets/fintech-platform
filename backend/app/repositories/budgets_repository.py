from sqlalchemy.orm import Session
from uuid import UUID

from app.models.budget import Budget


class BudgetsRepository:

    @staticmethod
    def create(db: Session, user_id: UUID, category_id: UUID, limit: float):

        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            limit=limit,
        )

        db.add(budget)
        db.commit()
        db.refresh(budget)

        return budget

    @staticmethod
    def get_by_user(db: Session, user_id: UUID):

        return (
            db.query(Budget)
            .filter(Budget.user_id == user_id)
            .all()
        )

    @staticmethod
    def get_by_category(db: Session, user_id: UUID, category_id: UUID):

        return (
            db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
            )
            .first()
        )