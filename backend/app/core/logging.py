import logging
from logging.config import dictConfig

from app.config.settings import settings


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                }
            },
            "root": {"handlers": ["default"], "level": settings.log_level.upper()},
        }
    )


logger = logging.getLogger("coffee-api")
