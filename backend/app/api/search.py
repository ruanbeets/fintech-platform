from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.deps import get_db
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
def global_search(user_id: UUID, query: str, db: Session = Depends(get_db)):

    return SearchService.global_search(db, user_id, query)