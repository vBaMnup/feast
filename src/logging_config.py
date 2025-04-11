import logging
import logging.config
import os

LOG_CONFIG_FILE = "logging.ini"


def setup_logging():
    """Setup logging configuration from a file."""

    if not os.path.exists(LOG_CONFIG_FILE):
        logging.error(f"Logging configuration file not found: {LOG_CONFIG_FILE}")
        return

    try:
        logging.config.fileConfig(LOG_CONFIG_FILE, disable_existing_loggers=False)
        logging.info(f"Logging configured successfully from {LOG_CONFIG_FILE}.")
    except Exception as e:
        logging.error(
            f"Failed to configure logging from {LOG_CONFIG_FILE}: {e}", exc_info=True
        )
