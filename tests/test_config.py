import pytest

from coffee_backend.core.config import Settings


def test_production_requires_non_default_jwt_secret() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(app_env="production", jwt_secret="dev-secret")


def test_cors_origins_parsing() -> None:
    settings = Settings(cors_allowed_origins="http://localhost:3000, https://coffee.example.com")
    assert settings.cors_allowed_origins == [
        "http://localhost:3000",
        "https://coffee.example.com",
    ]
