from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = Field(default="local", validation_alias="APP_ENV")
    database_url: str = Field(default="sqlite:///./coffee.db", validation_alias="DATABASE_URL")
    jwt_secret: str = Field(default="dev-secret", validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_expiry_minutes: int = Field(default=60, validation_alias="JWT_EXPIRY_MINUTES")
    demo_mode: bool = Field(default=False, validation_alias="DEMO_MODE")
    failed_brew_score: float = Field(default=0.0, validation_alias="FAILED_BREW_SCORE")
    optuna_skip_compatibility_check: bool = Field(
        default=True, validation_alias="OPTUNA_SKIP_COMPATIBILITY_CHECK"
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    cors_allowed_origins: list[str] = Field(
        default_factory=list,
        validation_alias="CORS_ALLOWED_ORIGINS",
    )
    enable_request_id_middleware: bool = Field(
        default=True,
        validation_alias="ENABLE_REQUEST_ID_MIDDLEWARE",
    )
    hash_time_cost: int = Field(default=3, validation_alias="HASH_TIME_COST")
    hash_memory_cost: int = Field(default=65536, validation_alias="HASH_MEMORY_COST")
    hash_parallelism: int = Field(default=4, validation_alias="HASH_PARALLELISM")

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
