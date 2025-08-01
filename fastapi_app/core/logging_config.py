import logging
import logging.handlers
import os
import sys

from fastapi import logger

class SuppressSelectorFilter(logging.Filter):
    def filter(self, record):
        if "Using selector: EpollSelector" in record.getMessage():
            logger.debug(f"Suppressed EpollSelector log from logger: {record.name}")
            return False
        return True

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "suppress_selector": {
            "()": SuppressSelectorFilter,
        },
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
            "level": "DEBUG",
            "filters": ["suppress_selector"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(os.path.dirname(__file__), "../../app.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "level": "INFO",
            "encoding": "utf-8",
            "filters": ["suppress_selector"],
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "my_app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "my_app.celery": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "my_app.vk_service": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "asyncio": {
            "level": "ERROR",
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "celery": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "aiogram": {
            "level": "DEBUG",  # Увеличим до DEBUG для отладки
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "aiohttp": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
        "sqlalchemy": {
            "level": "DEBUG",  # Добавим для отладки SQL-запросов
            "handlers": ["console", "file"],
            "propagate": False,
            "filters": ["suppress_selector"],
        },
    },
}

def setup_logging() -> None:
    log_dir = os.path.dirname(LOGGING_CONFIG["handlers"]["file"]["filename"])
    try:
        os.makedirs(log_dir, exist_ok=True)
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger("my_app")
        logger.debug("Logging setup completed successfully")
    except Exception as e:
        print(f"Failed to setup logging: {e}", file=sys.stderr)
        raise
