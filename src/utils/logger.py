"""
logger.py — one shared logger config for the whole project. Every module
does `from src.utils.logger import get_logger; log = get_logger(__name__)`
instead of configuring its own logging. Logs to logs/aicos.log + console.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    raise NotImplementedError
