"""
Error handling utilities.
Provides consistent error handling across the application.
"""

import logging
from functools import wraps
from typing import Callable, Any, Type

logger = logging.getLogger(__name__)


class SecureMediException(Exception):
    """Base exception for SecureMedi application."""

    pass


class BlockchainException(SecureMediException):
    """Raised when blockchain operations fail."""

    pass


class DetectorException(SecureMediException):
    """Raised when anomaly detection fails."""

    pass


class LoggerException(SecureMediException):
    """Raised when logging operations fail."""

    pass


def handle_errors(error_type: Type[BaseException] = Exception):
    """
    Decorator for consistent error handling.

    Args:
        error_type: Exception type to convert to SecureMediException
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except error_type as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise SecureMediException(f"Operation failed: {e}") from e
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                raise

        return wrapper

    return decorator
