from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class AccountCreate(BaseModel):
    name: str
    institution: str | None = None


class AccountUpdate(BaseModel):
    name: str | None = None
    institution: str | None = None


class AccountRead(BaseModel):
    id: UUID
    name: str
    institution: str | None
    created_at: datetime

    class Config:
        from_attributes = True