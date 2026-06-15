"""Structured logging middleware with correlation IDs."""

import logging
import uuid
from contextvars import ContextVar

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get()


class CorrelationFilter(logging.Filter):
    """Logging filter that adds correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


class StructuredFormatter(logging.Formatter):
    """Structured log formatter with correlation IDs."""

    def format(self, record: logging.LogRecord) -> str:
        # Add correlation ID if not present
        if not hasattr(record, "correlation_id"):
            record.correlation_id = get_correlation_id()

        # Format the log message
        return super().format(record)


def setup_structured_logging(
    level: int = logging.INFO,
    format_str: str | None = None,
) -> None:
    """Configure structured logging with correlation IDs.

    Args:
        level: Logging level (default: INFO)
        format_str: Custom format string (default: structured JSON-like format)
    """
    if format_str is None:
        format_str = "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Create formatter
    formatter = StructuredFormatter(format_str)
    handler.setFormatter(formatter)

    # Add correlation filter
    correlation_filter = CorrelationFilter()
    handler.addFilter(correlation_filter)

    # Add handler to root logger
    root_logger.addHandler(handler)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return uuid.uuid4().hex[:12]
