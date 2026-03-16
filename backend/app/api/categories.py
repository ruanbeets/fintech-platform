from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.categories_service import CategoriesService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/")
def create_category(name: str, db: Session = Depends(get_db)):

    return CategoriesService.create_category(db, name)


@router.get("/")
def get_categories(db: Session = Depends(get_db)):

    return CategoriesService.get_all_categories(db)


@router.get("/{category_id}")
def get_category(category_id: UUID, db: Session = Depends(get_db)):

    return CategoriesService.get_category(db, category_id)