import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.init_db import init_db
from app.api.transactions import router as transactions_router
from app.api.users import router as users_router
from app.api.accounts import router as accounts_router
from app.api.ingestion import router as ingestion_router

load_dotenv()

FRONTEND_URLS = os.getenv("FRONTEND_URLS", "http://localhost:3000")
origins = [origin.strip() for origin in FRONTEND_URLS.split(",")]

app = FastAPI(
    title="FinTrack API",
    description="Personal Finance Tracking API",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router, prefix="/api")
app.include_router(accounts_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(ingestion_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok"}