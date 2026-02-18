from sqlalchemy import select
from sqlalchemy.orm import Session

from coffee_backend.core.security import hash_password, verify_password
from coffee_backend.db.models.user import User
from coffee_backend.schemas.user import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, payload: UserCreate) -> User:
        user = User(
            email=payload.email, hashed_password=hash_password(payload.password), name=payload.name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.db.scalar(select(User).where(User.email == email))
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def list_users(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.created_at.desc())))
