"""
Backward compatibility wrapper for anomaly detection.
This module maintains backward compatibility with legacy code
that used to import directly from edge_ai.detector.
Now it delegates to the service layer.
"""

from typing import Dict, Any, Literal, Optional
from services.detector_service import DetectorService

# Create singleton instance for backward compatibility
_service_instance: Optional[DetectorService] = None


def _get_service() -> DetectorService:
    """Get or create detector service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = DetectorService()
    return _service_instance


# Expose service methods at module level
def detect(data: Dict[str, Any]) -> Literal["ALERT", "NORMAL"]:
    """Detect anomalies in health vitals. (Backward compat wrapper)"""
    return _get_service().detect(data)


def update_thresholds(
    heart_rate_max: Optional[int] = None,
    temperature_max: Optional[float] = None,
    spo2_min: Optional[int] = None,
) -> None:
    """Update detection thresholds at runtime. (Backward compat wrapper)"""
    return _get_service().update_thresholds(heart_rate_max, temperature_max, spo2_min)


def get_thresholds() -> Dict[str, Any]:
    """Get current thresholds. (Backward compat wrapper)"""
    return _get_service().get_thresholds()
