import bcrypt  # type: ignore[import-not-found]
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.users.models import Users


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  # type: ignore[no-any-return]


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())  # type: ignore[no-any-return]


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, username: str, email: str, password: str) -> Users:
        user = Users(username=username, email=email, password=hash_password(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id: int) -> Users | None:
        return self.db.get(Users, user_id)

    def get_user_by_email(self, email: str) -> Users | None:
        return self.db.scalar(select(Users).where(Users.email == email))

    def update_user(
        self,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> Users | None:
        user = self.get_user(user_id)
        if user is None:
            return None
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if password is not None:
            user.password = hash_password(password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> Users | None:
        user = self.get_user(user_id)
        if user is not None:
            self.db.delete(user)
            self.db.commit()
        return user

    def login_user(self, email: str, password: str) -> Users | None:
        user = self.get_user_by_email(email)
        return user if user and verify_password(password, user.password) else None
