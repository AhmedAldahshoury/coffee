from functools import lru_cache

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.db.session import get_db
from app.models.persistence import User
from app.repositories.csv_repository import CSVRepository
from app.services.auth_service import AuthService
from app.services.interactive_optimizer import InteractiveOptimizerService
from app.services.optimizer_service import OptimizerService

security = HTTPBearer(auto_error=False)


@lru_cache
def get_csv_repository() -> CSVRepository:
    return CSVRepository(data_dir=settings.data_dir)


@lru_cache
def get_optimizer_service() -> OptimizerService:
    return OptimizerService(seed=settings.seed)


def get_interactive_optimizer_service(db: Session = Depends(get_db)) -> InteractiveOptimizerService:
    return InteractiveOptimizerService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> User:
    raw_token = credentials.credentials if credentials else token
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = AuthService.decode_token(raw_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = db.get(User, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
