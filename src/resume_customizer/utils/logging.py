# ABOUTME: Structured logging configuration for the application
# ABOUTME: Provides logger creation, formatting, and context support

"""Logging configuration for resume customizer."""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Any, Dict


# Global flag to track if logging has been configured
_logging_configured = False


def reset_logging() -> None:
    """Reset logging configuration. Useful for testing."""
    global _logging_configured
    _logging_configured = False


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'message', 'pathname', 'process',
                          'processName', 'relativeCreated', 'thread', 'threadName',
                          'exc_info', 'exc_text', 'stack_info'):
                log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def configure_logging() -> None:
    """
    Configure logging for the application.
    
    This function sets up the root logger and application logger with
    appropriate handlers and formatters based on environment settings.
    """
    global _logging_configured
    
    # Get configuration from environment
    log_level_str = os.environ.get('RESUME_LOG_LEVEL', 'INFO').upper()
    log_format = os.environ.get('RESUME_LOG_FORMAT', 'standard')
    
    # Map string to logging level
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    log_level = level_map.get(log_level_str, logging.INFO)
    
    # Get the application logger
    logger = logging.getLogger('resume_customizer')
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Set formatter based on configuration
    if log_format == 'json':
        formatter = JSONFormatter()
    else:
        # Standard format with timestamp, level, and message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Set logger level
    logger.setLevel(log_level)
    
    # Don't propagate to root logger to avoid duplicate logs
    logger.propagate = True
    
    _logging_configured = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Optional name for child logger. If provided, creates a child
              logger under 'resume_customizer.{name}'
    
    Returns:
        Logger instance
    """
    # Configure logging if not already done
    if not _logging_configured:
        configure_logging()
    
    if name:
        logger_name = f'resume_customizer.{name}'
    else:
        logger_name = 'resume_customizer'
    
    return logging.getLogger(logger_name)