import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.transactions import router as transactions_router
from app.api.users import router as users_router
from app.api.accounts import router as accounts_router

# Load environment variables
load_dotenv()

# Get comma-separated frontend URLs
FRONTEND_URLS = os.getenv("FRONTEND_URLS", "http://localhost:3000")
origins = [origin.strip() for origin in FRONTEND_URLS.split(",")]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router)
app.include_router(users_router)
app.include_router(accounts_router)


@app.get("/")
def health_check():
    return {"status": "ok"}