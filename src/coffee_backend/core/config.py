from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "local"
    database_url: str = "sqlite:///./coffee.db"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60
    demo_mode: bool = False
    failed_brew_score: float = 0.0
    optuna_skip_compatibility_check: bool = True
    log_level: str = "INFO"
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    enable_request_id_middleware: bool = True
    hash_time_cost: int = 3
    hash_memory_cost: int = 65536
    hash_parallelism: int = 4

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            if not value.strip():
                return []
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env.lower() in {"prod", "production"} and self.jwt_secret in {
            "",
            "dev-secret",
            "change-me",
        }:
            raise ValueError("JWT_SECRET must be set to a strong value in production")

        if self.hash_time_cost < 2 or self.hash_memory_cost < 19456 or self.hash_parallelism < 1:
            raise ValueError("Password hash settings are too weak")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
