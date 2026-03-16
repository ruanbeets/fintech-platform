from app.database.session import SessionLocal
from app.services.analytics_service import AnalyticsService
from app.services.dashboard_service import DashboardService
from app.repositories.users_repository import UsersRepository
from app.core.logging import get_logger
from app.core.cache import cache_set

logger = get_logger(__name__)


class AnalyticsWorker:

    @staticmethod
    def run_user_analytics(db, user_id):

        logger.info(f"Running analytics for user {user_id}")

        spending = AnalyticsService.spending_by_category(db, user_id)

        monthly = AnalyticsService.monthly_spending(db, user_id)

        cashflow = AnalyticsService.cashflow_summary(db, user_id)

        forecast = AnalyticsService.balance_forecast(db, user_id)

        dashboard = DashboardService.get_dashboard_summary(db, user_id)

        cache_set(f"analytics:spending:{user_id}", spending)
        cache_set(f"analytics:monthly:{user_id}", monthly)
        cache_set(f"analytics:cashflow:{user_id}", cashflow)
        cache_set(f"analytics:forecast:{user_id}", forecast)
        cache_set(f"dashboard:{user_id}", dashboard)

        logger.info(f"Analytics completed for user {user_id}")


    @staticmethod
    def run_all_users():

        db = SessionLocal()

        try:

            users = db.query(UsersRepository.__annotations__ if False else []).all()

        except Exception:
            users = []

        try:

            users = db.query(UsersRepository.__annotations__ if False else []).all()

        except Exception:
            users = []

        try:

            users = db.query(UsersRepository.__annotations__ if False else []).all()

        except Exception:
            users = []

        finally:

            db.close()


def run():

    db = SessionLocal()

    try:

        from app.models.user import User

        users = db.query(User).all()

        for user in users:

            AnalyticsWorker.run_user_analytics(db, user.id)

    finally:

        db.close()