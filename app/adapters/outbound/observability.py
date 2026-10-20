"""Adaptateur du port EventPublisher : logs JSON lus par Cloud Logging.

Cloud Run transmet la sortie standard à Cloud Logging. Les champs "severity",
"message" et "logging.googleapis.com/trace" y sont reconnus ; les autres
atterrissent dans jsonPayload, puis dans BigQuery via le sink d'audit.
"""
from __future__ import annotations

import json
import logging
import sys

from app.adapters.shared.tracing import trace_id

LOGGER_NAME = "diag"


class JsonFormatter(logging.Formatter):
    def __init__(self, project: str = ""):
        super().__init__()
        self._project = project

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            payload.update(fields)
        current = trace_id.get()
        if current and self._project:
            payload["logging.googleapis.com/trace"] = f"projects/{self._project}/traces/{current}"
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_json_logging(project: str) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(project))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


class LoggingEventPublisher:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def publish(self, name: str, level: str = "INFO", **fields: object) -> None:
        self._logger.log(logging.getLevelName(level), name,
                         extra={"fields": {"event": name, **fields}})
