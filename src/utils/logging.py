from __future__ import annotations

import json
import logging
from typing import Any

SENSITIVE_KEYS = {"authorization", "token", "api_key", "password", "secret"}


def _sanitize(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in SENSITIVE_KEYS:
            redacted[key] = "***REDACTED***"
        else:
            redacted[key] = value
    return redacted


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format="%(message)s")


class StructuredLogger:
    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)

    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(json.dumps({"level": "INFO", "message": message, **_sanitize(kwargs)}))

    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(json.dumps({"level": "ERROR", "message": message, **_sanitize(kwargs)}))

    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(json.dumps({"level": "WARNING", "message": message, **_sanitize(kwargs)}))
