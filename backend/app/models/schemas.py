from uuid import UUID
from datetime import date
from pydantic import BaseModel

class TransactionCreate(BaseModel):
    user_id: UUID
    account_id: UUID
    date: date
    amount: float
    category: str | None = None
    description: str | None = None


class TransactionResponse(BaseModel):
    transaction_id: UUID
    user_id: UUID
    account_id: UUID
    date: date
    amount: float
    category: str | None = None
    description: str | None = None

    class Config:
        from_attributes = True