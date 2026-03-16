from sqlalchemy.orm import declarative_base


Base = declarative_base()


# Import all models here so SQLAlchemy registers them
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category
from app.models.budget import Budget
from app.models.notification import Notification
from app.models.audit_log import AuditLog