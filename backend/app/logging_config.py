"""
Structured JSON logging configuration for the AI Resume Analyser API.

Provides request-scoped trace IDs and JSON-formatted log output for
production observability across parsing, AI inference, and fallback paths.
"""

import logging
import json
import uuid
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Custom JSON log formatter that outputs structured log records
    compatible with cloud logging platforms (e.g., GCP Cloud Logging).
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach request_id if available on the log record
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        # Attach extra fields if provided
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        # Attach exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configures the root logger with JSON-structured output.

    :param log_level: Logging level string (e.g., 'DEBUG', 'INFO', 'WARNING')
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers to prevent duplicate log entries
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def generate_request_id() -> str:
    """Generates a unique request trace ID."""
    return str(uuid.uuid4())[:8]
