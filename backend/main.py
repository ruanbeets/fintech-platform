from fastapi import FastAPI
from backend.app.api.transactions import router as transactions_router

app = FastAPI()

app.include_router(transactions_router)

@app.get("/")
def health_check():
    return {"status": "ok"}