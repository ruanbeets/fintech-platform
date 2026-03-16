from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class NotificationRead(BaseModel):
    id: UUID
    message: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    read: bool