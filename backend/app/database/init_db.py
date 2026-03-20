from app.database.base import Base
from app.database.connection import engine

# IMPORTANT: import models so SQLAlchemy registers them
from app.models import user, account, transaction


def init_db():
    Base.metadata.create_all(bind=engine)