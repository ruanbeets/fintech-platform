from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.users_repository import UsersRepository


class SettingsService:

    @staticmethod
    def get_user_settings(db: Session, user_id: UUID):

        user = UsersRepository.get_by_id(db, user_id)

        if not user:
            raise ValueError("User not found")

        return {
            "email": user.email,
            "role": user.role
        }


    @staticmethod
    def update_user_email(db: Session, user_id: UUID, email: str):

        user = UsersRepository.get_by_id(db, user_id)

        if not user:
            raise ValueError("User not found")

        user.email = email

        db.commit()

        return user