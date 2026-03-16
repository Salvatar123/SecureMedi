"""
Edge AI module - Local anomaly detection and sensor data generation.
"""

from .sensor import generate_data
from .detector import detect, update_thresholds, get_thresholds

__all__ = [
    "generate_data",
    "detect",
    "update_thresholds",
    "get_thresholds",
]
