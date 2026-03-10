from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User


def create_user(db: Session, email: str) -> User:
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session):
    return db.query(User).all()


def delete_user(db: Session, user_id: UUID):
    user = db.query(User).filter(User.user_id == user_id).first()

    if user:
        db.delete(user)
        db.commit()

    return user