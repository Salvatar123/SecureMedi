"""
Backward compatibility wrapper for logger operations.
This module maintains backward compatibility with legacy code
that used to import directly from logger.
Now it delegates to the service layer.
"""

from typing import Optional, Dict, Any, List
from services.logger_service import LoggerService

# Create singleton instance for backward compatibility
_service_instance: Optional[LoggerService] = None


def _get_service() -> LoggerService:
    """Get or create logger service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = LoggerService()
    return _service_instance


# Expose service methods at module level
def save(data: Dict[str, Any], status: str) -> None:
    """Save health data and status to CSV. (Backward compat wrapper)"""
    return _get_service().save(data, status)


def get_latest_records(limit: int = 10) -> List[Dict[str, Any]]:
    """Get the latest N records from the log. (Backward compat wrapper)"""
    return _get_service().get_latest_records(limit)


def get_statistics() -> Dict[str, Any]:
    """Get statistics from all logged data. (Backward compat wrapper)"""
    return _get_service().get_statistics()


def clear_logs() -> None:
    """Clear all log entries (use with caution). (Backward compat wrapper)"""
    return _get_service().clear_logs()
