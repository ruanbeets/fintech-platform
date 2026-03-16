from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.categories_repository import CategoriesRepository


class CategoriesService:

    @staticmethod
    def create_category(db: Session, name: str):

        return CategoriesRepository.create(db, name)


    @staticmethod
    def get_all_categories(db: Session):

        return CategoriesRepository.get_all(db)


    @staticmethod
    def get_category(db: Session, category_id: UUID):

        category = CategoriesRepository.get_by_id(db, category_id)

        if not category:
            raise ValueError("Category not found")

        return category