"""Logging utilities for structured output."""
from __future__ import annotations

import json
import logging
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """Simple JSON log formatter with ISO timestamps."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting logic
        base = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)


def configure(level: int = logging.INFO) -> None:
    """Configure root logger for the entire project."""

    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
    root.setLevel(level)
