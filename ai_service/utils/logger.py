"""
Structured logging configuration using structlog
"""

import logging
import sys
from typing import Any
import structlog
from pythonjsonlogger import jsonlogger

from config import settings


def setup_logging():
    """
    Configure structured logging with structlog and JSON formatting
    
    This creates logs in JSON format for easy parsing by log aggregation tools
    """
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )
    
    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add JSON formatting for production
    if settings.LOG_FORMAT.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Use console rendering for development
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> Any:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Structured logger
    """
    return structlog.get_logger(name)


class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for standard logging"""
    
    def add_fields(self, log_record, record, message_dict):
        super(JSONFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add custom fields
        log_record['timestamp'] = log_record.get('asctime')
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        
        # Remove default fields we don't need
        log_record.pop('asctime', None)
        log_record.pop('levelname', None)
        log_record.pop('name', None)