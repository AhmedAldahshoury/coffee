from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    database_url: str = "sqlite:///./coffee.db"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60
    demo_mode: bool = False
    failed_brew_score: float = 0.0
    optuna_skip_compatibility_check: bool = True
    log_level: str = "INFO"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
