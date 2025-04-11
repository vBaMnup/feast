import logging
import sys

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
CONSOLE_LOG_LEVEL = "INFO"
FILE_LOG_LEVEL = "DEBUG"
LOG_FILE = "app.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": CONSOLE_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout,
        },
        "file": {
            "level": FILE_LOG_LEVEL,
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": LOG_FILE,
            "encoding": "utf-8",
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": FILE_LOG_LEVEL,
            "propagate": True,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "src": {
            "handlers": ["console", "file"],
            "level": FILE_LOG_LEVEL,
            "propagate": False,
        },
    },
}


def setup_logging():
    """Application logging configuration."""

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info(
        "Logging configured successfully. Console level: %s, File level: %s",
        CONSOLE_LOG_LEVEL,
        FILE_LOG_LEVEL,
    )
