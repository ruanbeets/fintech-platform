from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User


class UsersRepository:

    @staticmethod
    def create(db: Session, email: str, hashed_password: str):

        user = User(
            email=email,
            hashed_password=hashed_password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_by_id(db: Session, user_id: UUID):

        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str):

        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def delete(db: Session, user_id: UUID):

        user = db.query(User).filter(User.id == user_id).first()

        if user:
            db.delete(user)
            db.commit()

        return user