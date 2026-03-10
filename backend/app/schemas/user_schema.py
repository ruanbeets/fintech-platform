from uuid import UUID
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str


class UserResponse(BaseModel):
    user_id: UUID
    email: str

    class Config:
        from_attributes = True