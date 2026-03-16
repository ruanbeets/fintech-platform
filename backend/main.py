import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from app.core.config import settings
from app.core.logging import setup_logging, get_logger

from app.database.init_db import init_db

from app.api import (
    auth,
    users,
    accounts,
    transactions,
    analytics,
    dashboard,
    budgets,
    categories,
    notifications,
    reports,
    search,
    user_settings,
    ingestion,
)

# --------------------------------------------------
# Logging Setup
# --------------------------------------------------

setup_logging()
logger = get_logger(__name__)


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Financial analytics and personal finance platform",
)


# --------------------------------------------------
# CORS Middleware
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Database Wait Function
# --------------------------------------------------

def wait_for_database():

    logger.info("Waiting for database connection...")

    retries = 10
    delay = 3

    for attempt in range(retries):

        try:

            engine = create_engine(settings.DATABASE_URL)

            with engine.connect():
                logger.info("Database connection established")
                return

        except Exception:

            logger.warning(
                f"Database not ready (attempt {attempt+1}/{retries}), retrying..."
            )

            time.sleep(delay)

    raise RuntimeError("Database connection failed after multiple retries")


# --------------------------------------------------
# Startup Event
# --------------------------------------------------

@app.on_event("startup")
def startup_event():

    logger.info("Starting Fintech Platform")

    try:

        wait_for_database()

        init_db()

        logger.info("Database initialized")

    except Exception as e:

        logger.error(f"Database initialization failed: {e}")

        raise


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Fintech Platform API",
        "version": "1.0.0",
    }


# --------------------------------------------------
# API Routers
# --------------------------------------------------

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(dashboard.router)
app.include_router(budgets.router)
app.include_router(categories.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(search.router)
app.include_router(user_settings.router)
app.include_router(ingestion.router)


# --------------------------------------------------
# Shutdown Event
# --------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():

    logger.info("Shutting down Fintech Platform")