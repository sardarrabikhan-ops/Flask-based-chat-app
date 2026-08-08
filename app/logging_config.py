# app/logging_config.py

import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path


def configure_logging() -> None:

    logs_directory = Path("logs")
    logs_directory.mkdir(exist_ok=True)

    log_file = logs_directory / "app.log"

    logger = logging.getLogger()

    already_configured = any(
        isinstance(h, RotatingFileHandler) or type(h) is logging.StreamHandler
        for h in logger.handlers
    )

    if already_configured:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)
