from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TransactionCreate(BaseModel):
    description: str | None = None
    amount: float
    type: str
    account_id: UUID
    category_id: UUID | None = None


class TransactionUpdate(BaseModel):
    description: str | None = None
    amount: float | None = None
    category_id: UUID | None = None


class TransactionRead(BaseModel):
    id: UUID
    description: str | None
    amount: float
    type: str
    date: datetime
    account_id: UUID
    category_id: UUID | None

    class Config:
        from_attributes = True