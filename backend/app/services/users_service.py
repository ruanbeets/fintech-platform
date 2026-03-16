from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.users_repository import UsersRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth_schema import Token


class UsersService:

    @staticmethod
    def register_user(db: Session, email: str, password: str):

        existing = UsersRepository.get_by_email(db, email)

        if existing:
            raise ValueError("User already exists")

        hashed = hash_password(password)

        user = UsersRepository.create(db, email, hashed)

        return user


    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):

        user = UsersRepository.get_by_email(db, email)

        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        token = create_access_token({
            "user_id": str(user.id),
            "role": user.role
        })

        return Token(
            access_token=token
        )


    @staticmethod
    def get_user(db: Session, user_id: UUID):

        user = UsersRepository.get_by_id(db, user_id)

        if not user:
            raise ValueError("User not found")

        return user


    @staticmethod
    def delete_user(db: Session, user_id: UUID):

        user = UsersRepository.delete(db, user_id)

        if not user:
            raise ValueError("User not found")

        return user