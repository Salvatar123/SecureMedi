"""Sensor data generation module for testing and simulation."""

import random
from typing import Dict, Any


def generate_data() -> Dict[str, Any]:
    """Generate simulated sensor data for testing.

    Returns:
        Dictionary with heart rate (bpm), temperature (°C), and SpO2 (%)
    """
    return {
        "heart": random.randint(60, 130),
        "temp": round(random.uniform(36, 39.5), 1),
        "spo2": random.randint(88, 100),
    }
