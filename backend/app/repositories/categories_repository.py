from sqlalchemy.orm import Session
from uuid import UUID

from app.models.category import Category


class CategoriesRepository:

    @staticmethod
    def create(db: Session, name: str):

        category = Category(name=name)

        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def get_all(db: Session):

        return db.query(Category).all()

    @staticmethod
    def get_by_id(db: Session, category_id: UUID):

        return (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )