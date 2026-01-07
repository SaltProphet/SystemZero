"""Structured logging for System//Zero with JSON output and contextual fields."""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variable for request-scoped data
_log_context: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add context from ContextVar
        context = _log_context.get()
        if context:
            log_data["context"] = context
        
        return json.dumps(log_data)


class ContextLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context to log records."""
    
    def process(self, msg: str, kwargs: Any) -> tuple:
        """Add context to kwargs."""
        extra = kwargs.get("extra", {})
        
        # Merge with context
        context = _log_context.get()
        if context:
            extra["extra_fields"] = {**context, **extra.get("extra_fields", {})}
        elif "extra_fields" in extra:
            pass  # Keep existing extra_fields
        else:
            extra["extra_fields"] = {}
        
        kwargs["extra"] = extra
        return msg, kwargs


def configure_logging(
    level: str = "INFO",
    json_output: bool = True,
    log_file: Optional[Path] = None
) -> None:
    """Configure structured logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Use JSON formatter if True, else standard formatter
        log_file: Optional file path for file logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if json_output:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> ContextLoggerAdapter:
    """Get a logger with context support.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        ContextLoggerAdapter instance
    """
    logger = logging.getLogger(name)
    return ContextLoggerAdapter(logger, {})


def add_context(**kwargs: Any) -> None:
    """Add fields to the current log context.
    
    Context is stored in a ContextVar and automatically included in all logs
    within the same async context.
    
    Example:
        add_context(request_id="abc123", user="admin", endpoint="/api/status")
        logger.info("Processing request")  # Will include request_id, user, endpoint
    """
    current = _log_context.get()
    _log_context.set({**current, **kwargs})


def clear_context() -> None:
    """Clear the current log context."""
    _log_context.set({})


def get_context() -> Dict[str, Any]:
    """Get the current log context."""
    return _log_context.get()
