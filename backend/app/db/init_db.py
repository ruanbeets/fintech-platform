from backend.app.db.base import Base
from backend.app.db.session import engine

# Import models so SQLAlchemy registers them
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.transaction import Transaction


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Tables created successfully.")