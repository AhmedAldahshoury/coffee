from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Coffee Optimizer API"
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    data_dir: str = Field(default="./data")
    seed: int = Field(default=42)
    optimizer_prior_weight: float = Field(default=0.666)
    database_url: str = Field(default="sqlite:///./coffee.db")
    jwt_secret: str = Field(default="dev-secret")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=60 * 24)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
