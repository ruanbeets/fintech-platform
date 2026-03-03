from fastapi import FastAPI
from backend.app.api.transactions import router as transactions_router
from backend.app.api.users import router as users_router
from backend.app.api.accounts import router as accounts_router

app = FastAPI()

app.include_router(transactions_router)
app.include_router(users_router)
app.include_router(accounts_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
