from app.database.base import Base
from app.database.session import engine

# Import models so SQLAlchemy registers them
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Tables created successfully.")