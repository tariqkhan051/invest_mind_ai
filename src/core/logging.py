"""Structured logging configuration using Loguru.

See docs/03_ARCHITECTURE.md §21 and docs/23_AI_DEVELOPMENT_GUIDE.md §15.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from loguru import logger

from src.config.settings import Settings

_LOGGING_CONFIGURED = False


def _ensure_log_directories(settings: Settings) -> None:
    """Create log directories defined in logging configuration."""
    sinks = settings.logging_config.get("sinks", {})
    for sink_path in sinks.values():
        Path(sink_path).parent.mkdir(parents=True, exist_ok=True)

    default_dirs = [
        "logs/application",
        "logs/scheduler",
        "logs/ai",
        "logs/imports",
        "logs/notifications",
        "logs/errors",
    ]
    for directory in default_dirs:
        (settings.project_root / directory).mkdir(parents=True, exist_ok=True)


def setup_logging(settings: Settings) -> None:
    """Configure application logging once at startup."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    _ensure_log_directories(settings)
    logger.remove()

    default_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
        "{name}:{function}:{line} | {message}"
    )
    log_format = settings.logging_config.get("format", default_format)

    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=log_format,
        colorize=True,
        enqueue=True,
    )

    if not settings.is_testing:
        sinks = settings.logging_config.get("sinks", {})
        rotation = settings.yaml_config.get("logging", {}).get("rotation", "10 MB")
        retention = settings.yaml_config.get("logging", {}).get("retention", "7 days")

        for sink_name, sink_path in sinks.items():
            level = settings.logging_config.get("levels", {}).get(sink_name, "INFO")
            logger.add(
                str(settings.project_root / sink_path),
                level=level,
                format=log_format,
                rotation=rotation,
                retention=retention,
                enqueue=True,
            )

    _LOGGING_CONFIGURED = True
    logger.info("Logging configured for environment={}", settings.environment)


def get_logger(name: str) -> Any:
    """Return a named logger instance."""
    return logger.bind(module=name)
