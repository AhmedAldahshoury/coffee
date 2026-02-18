from datetime import datetime, timedelta, timezone
from functools import lru_cache
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from jose import JWTError, jwt

from coffee_backend.core.config import get_settings


@lru_cache(maxsize=1)
def get_password_hasher() -> PasswordHasher:
    settings = get_settings()
    return PasswordHasher(
        time_cost=settings.hash_time_cost,
        memory_cost=settings.hash_memory_cost,
        parallelism=settings.hash_parallelism,
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_hasher = get_password_hasher()
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def hash_password(password: str) -> str:
    return get_password_hasher().hash(password)


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Invalid token payload")
        return UUID(sub)
    except (JWTError, ValueError) as exc:
        raise ValueError("Invalid authentication token") from exc
