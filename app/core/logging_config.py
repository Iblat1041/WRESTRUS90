import logging
import logging.config
import logging.handlers
import os
import sys


class SuppressSelectorFilter(logging.Filter):
    def filter(self, record):
        return "Using selector: EpollSelector" not in record.getMessage()


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"suppress_selector": {"()": SuppressSelectorFilter}},
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
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
        "": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "asyncio": {"level": "ERROR", "handlers": ["console", "file"], "propagate": False},
        "aiogram": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "aiohttp": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "sqlalchemy": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "my_app": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "my_app.celery": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "my_app.vk_service": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
    },
}


def setup_logging() -> None:
    log_dir = os.path.dirname(LOGGING_CONFIG["handlers"]["file"]["filename"])
    try:
        os.makedirs(log_dir, exist_ok=True)
        logging.config.dictConfig(LOGGING_CONFIG)
        logging.getLogger("my_app").debug("Logging setup completed successfully")
    except Exception as e:
        print(f"Failed to setup logging: {e}", file=sys.stderr)
        raise
