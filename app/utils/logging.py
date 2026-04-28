"""Logging configuration for the SMS CLI client."""

import logging
import os

ROOT_NAME = "sms"
LOG_FILE = os.path.join("logs", f"{ROOT_NAME}.log")


def get_logger(name: str = "") -> logging.Logger:
    """Returns a logger that writes to `logs/sms.log`.

    All loggers share a single file via the `sms` root logger.

    Args:
        name: Optional suffix appended to the root name.

    Returns:
        A configured logger instance.
    """
    root = logging.getLogger(ROOT_NAME)

    if not root.handlers:
        os.makedirs("logs", exist_ok=True)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] <`%(name)s` module>: %(message)s"))
        root.setLevel(logging.DEBUG)
        root.addHandler(handler)

    return logging.getLogger(f"{ROOT_NAME}.{name}") if name else root
