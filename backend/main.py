import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from app.core.config import settings
from app.database.init_db import init_db

# Only include what you have actually built
from app.views import (
    auth_view,
    users_view,
    accounts_view,
    transactions_view,
    dashboard_view,
    settings_view,
)


# --------------------------------------------------
# App
# --------------------------------------------------

app = FastAPI(
    title="FinPlan Backend",
    version="1.0.0",
    description="FinPlan Backend (MVVM)",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# DB Wait
# --------------------------------------------------

def wait_for_database():
    print("Waiting for database...")

    retries = 10
    delay = 3

    for attempt in range(retries):
        try:
            engine = create_engine(settings.database_url)

            with engine.connect():
                print("Database connected")
                return

        except Exception:
            print(f"DB not ready ({attempt+1}/{retries}), retrying...")
            time.sleep(delay)

    raise RuntimeError("Database connection failed")


# --------------------------------------------------
# Startup
# --------------------------------------------------

@app.on_event("startup")
def startup_event():
    print("Starting FinPlan...")

    wait_for_database()
    init_db()

    print("Database ready")


# --------------------------------------------------
# Shutdown
# --------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down FinPlan...")


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FinPlan Backend",
    }


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "FinPlan API",
        "version": "1.0.0",
    }


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(auth_view.router)
app.include_router(users_view.router)
app.include_router(accounts_view.router)
app.include_router(transactions_view.router)
app.include_router(dashboard_view.router)
app.include_router(settings_view.router)