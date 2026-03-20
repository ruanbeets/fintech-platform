from app.database.connection import SessionLocal
from app.models.user import User


class UsersViewModel:

    @staticmethod
    def create_user(data: dict):
        db = SessionLocal()
        try:
            user = User(
                email=data["email"],
                password_hash=data["password_hash"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def get_user(user_id: str):
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    @staticmethod
    def get_users():
        db = SessionLocal()
        try:
            return db.query(User).all()
        finally:
            db.close()

    @staticmethod
    def update_user(user_id: str, data: dict):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            for key, value in data.items():
                setattr(user, key, value)

            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def delete_user(user_id: str):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            db.delete(user)
            db.commit()
            return True
        finally:
            db.close()