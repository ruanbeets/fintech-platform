from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.users_repository import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_all_users,
    delete_user
)


def create_new_user(db: Session, email: str):
    existing = get_user_by_email(db, email)

    if existing:
        raise ValueError("User already exists")

    return create_user(db, email)


def fetch_user(db: Session, user_id: UUID):
    user = get_user_by_id(db, user_id)

    if not user:
        raise ValueError("User not found")

    return user


def list_users(db: Session):
    return get_all_users(db)


def remove_user(db: Session, user_id: UUID):
    return delete_user(db, user_id)