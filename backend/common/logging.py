"""Structured logging setup for all platform services."""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml

from backend.config.settings import LOG_LEVEL

_CONFIGURED = False


def setup_logging() -> logging.Logger:
    """Configure application logging once and return the root logger."""
    global _CONFIGURED

    if not _CONFIGURED:
        config_path = Path(__file__).resolve().parents[2] / "config" / "logging.yaml"
        if config_path.exists():
            with config_path.open(encoding="utf-8") as handle:
                config = yaml.safe_load(handle)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(
                level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
                format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            )

        logging.getLogger().setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        _CONFIGURED = True

    return logging.getLogger()


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, ensuring logging is configured."""
    setup_logging()
    return logging.getLogger(name)
