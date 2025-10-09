"""
Centralized logging configuration for SubmitEZ.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context."""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def setup_logger(
    app,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    enable_json: bool = False
):
    """
    Setup application logging with file and console handlers.
    
    Args:
        app: Flask application instance
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log message format string
        enable_json: Enable JSON structured logging
    """
    
    # Get configuration
    log_level = log_level or app.config.get('LOG_LEVEL', 'INFO')
    log_format = log_format or app.config.get(
        'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    app.logger.setLevel(level)
    
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if enable_json:
        console_formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        console_formatter = logging.Formatter(log_format)
    
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)
    
    # File handler (production only)
    if not app.debug and not app.testing:
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Main log file with rotation
        file_handler = RotatingFileHandler(
            logs_dir / 'submitez.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(level)
        
        if enable_json:
            file_formatter = CustomJsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s'
            )
        else:
            file_formatter = logging.Formatter(log_format)
        
        file_handler.setFormatter(file_formatter)
        app.logger.addHandler(file_handler)
        
        # Error log file
        error_handler = RotatingFileHandler(
            logs_dir / 'error.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        app.logger.addHandler(error_handler)
        
        # Daily rotating log
        daily_handler = TimedRotatingFileHandler(
            logs_dir / 'daily.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        daily_handler.setLevel(level)
        daily_handler.setFormatter(file_formatter)
        app.logger.addHandler(daily_handler)
    
    app.logger.info(f"Logging initialized at {log_level} level")
    
    return app.logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (usually __name__)
        level: Optional logging level
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    return logger


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


def log_function_call(func):
    """Decorator to log function calls."""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
            raise
    
    return wrapper


def log_execution_time(func):
    """Decorator to log function execution time."""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.3f}s: {e}"
            )
            raise
    
    return wrapper