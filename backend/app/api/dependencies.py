from functools import lru_cache

from app.config.settings import settings
from app.repositories.csv_repository import CSVRepository
from app.services.optimizer_service import OptimizerService


@lru_cache
def get_csv_repository() -> CSVRepository:
    return CSVRepository(data_dir=settings.data_dir)


@lru_cache
def get_optimizer_service() -> OptimizerService:
    return OptimizerService(seed=settings.seed)
