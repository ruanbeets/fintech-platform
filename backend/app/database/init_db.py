from app.database.base import Base
from app.database.connection import engine
from app.core.config import settings
from sqlalchemy import text

# IMPORTANT: import models so SQLAlchemy registers them
from app.models import user, account, transaction
from app.models import imports


def init_db():
    Base.metadata.create_all(bind=engine)
    if settings.demo_mode and engine.dialect.name == "postgresql":
        # Supabase's anonymous Data API must not bypass session-scoped FastAPI.
        # The backend connects as table owner; no browser role gets an RLS policy.
        with engine.begin() as connection:
            for table in Base.metadata.sorted_tables:
                quoted = engine.dialect.identifier_preparer.quote(table.name)
                connection.execute(text(f"ALTER TABLE {quoted} ENABLE ROW LEVEL SECURITY"))
