from sqlalchemy.orm import Session

from app.database.session import engine
from app.database.base import Base

from app.models.category import Category


def init_db():

    Base.metadata.create_all(bind=engine)


def seed_categories(db: Session):

    default_categories = [
        "Food",
        "Transport",
        "Rent",
        "Utilities",
        "Entertainment",
        "Healthcare",
        "Shopping",
        "Income",
        "Other",
    ]

    for name in default_categories:

        category = Category(name=name)

        db.add(category)

    db.commit()