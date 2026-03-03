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


# -----------------
# USER
# -----------------

class UserCreate(BaseModel):
    email: str


class UserResponse(BaseModel):
    user_id: UUID
    email: str

    class Config:
        from_attributes = True


# -----------------
# ACCOUNT
# -----------------

class AccountCreate(BaseModel):
    user_id: UUID
    account_type: str
    currency: str


class AccountResponse(BaseModel):
    account_id: UUID
    user_id: UUID
    account_type: str
    currency: str

    class Config:
        from_attributes = True