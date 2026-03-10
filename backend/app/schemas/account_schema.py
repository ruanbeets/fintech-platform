from uuid import UUID
from pydantic import BaseModel


class AccountCreate(BaseModel):
    user_id: UUID
    account_type: str
    currency: str


class AccountResponse(BaseModel):
    account_id: UUID
    user_id: UUID
    account_type: str
    currency: str
    balance: float | None = 0

    class Config:
        from_attributes = True