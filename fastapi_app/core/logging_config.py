import logging
import logging.handlers
import os

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
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
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(os.path.dirname(__file__), "../../app.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "level": "INFO",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "my_app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "my_app.celery": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "my_app.vk_service": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "my_app.init_db": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "aiogram": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "celery": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "celery.task": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}

def setup_logging() -> None:
    """Настраивает логирование на основе конфигурации LOGGING_CONFIG."""
    log_file = LOGGING_CONFIG["handlers"]["file"]["filename"]
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)