"""
Structured logging setup using structlog.
"""
import structlog
import logging
import sys
from typing import Any, Dict

from qa_agent.core.config import settings


def configure_logging() -> None:
    """Configure structured logging."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_run_event(
    logger: structlog.BoundLogger,
    run_id: str,
    event_type: str,
    **kwargs: Any
) -> None:
    """Log a run-related event with structured data."""
    logger.info(
        "run_event",
        run_id=run_id,
        event_type=event_type,
        **kwargs
    )


def log_step_event(
    logger: structlog.BoundLogger,
    run_id: str,
    step_index: int,
    event_type: str,
    **kwargs: Any
) -> None:
    """Log a step-related event with structured data."""
    logger.info(
        "step_event",
        run_id=run_id,
        step_index=step_index,
        event_type=event_type,
        **kwargs
    )


def log_friction_event(
    logger: structlog.BoundLogger,
    run_id: str,
    friction_type: str,
    severity: str,
    score: float,
    **kwargs: Any
) -> None:
    """Log a friction detection event."""
    logger.warning(
        "friction_detected",
        run_id=run_id,
        friction_type=friction_type,
        severity=severity,
        score=score,
        **kwargs
    )
