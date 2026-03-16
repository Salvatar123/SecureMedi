"""
Detector service layer.
Wraps anomaly detection with configurable thresholds.
"""

import logging
from typing import Dict, Any, Literal, Optional
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DetectorService:
    """Service for anomaly detection in health vitals."""

    def __init__(
        self,
        heart_rate_max: Optional[int] = None,
        temperature_max: Optional[float] = None,
        spo2_min: Optional[int] = None,
    ):
        """
        Initialize detector with configurable thresholds.

        Args:
            heart_rate_max: Maximum normal heart rate (bpm)
            temperature_max: Maximum normal temperature (°C)
            spo2_min: Minimum normal blood oxygen (%)
        """
        self.heart_rate_max = heart_rate_max or settings.HEART_RATE_MAX
        self.temperature_max = temperature_max or settings.TEMPERATURE_MAX
        self.spo2_min = spo2_min or settings.SPO2_MIN

        logger.info(
            f"Detector initialized with thresholds: "
            f"HR>{self.heart_rate_max}, Temp>{self.temperature_max}, SpO2<{self.spo2_min}"
        )

    def detect(self, data: Dict[str, Any]) -> Literal["ALERT", "NORMAL"]:
        """
        Detect anomalies in health vitals.

        Args:
            data: Dictionary with heart, temp, spo2 values

        Returns:
            "ALERT" if any vital is abnormal, "NORMAL" otherwise
        """
        try:
            heart = data.get("heart", 0)
            temp = data.get("temp", 0)
            spo2 = data.get("spo2", 100)

            if heart > self.heart_rate_max:
                logger.warning(f"Alert: Heart rate {heart} > {self.heart_rate_max}")
                return "ALERT"

            if temp > self.temperature_max:
                logger.warning(f"Alert: Temperature {temp} > {self.temperature_max}")
                return "ALERT"

            if spo2 < self.spo2_min:
                logger.warning(f"Alert: SpO2 {spo2} < {self.spo2_min}")
                return "ALERT"

            return "NORMAL"

        except Exception as e:
            logger.error(f"Detection error: {e}")
            raise

    def update_thresholds(
        self,
        heart_rate_max: Optional[int] = None,
        temperature_max: Optional[float] = None,
        spo2_min: Optional[int] = None,
    ) -> None:
        """
        Update detection thresholds at runtime.

        Args:
            heart_rate_max: New maximum heart rate
            temperature_max: New maximum temperature
            spo2_min: New minimum SpO2
        """
        if heart_rate_max is not None:
            self.heart_rate_max = heart_rate_max
        if temperature_max is not None:
            self.temperature_max = temperature_max
        if spo2_min is not None:
            self.spo2_min = spo2_min

        logger.info(
            f"Thresholds updated: "
            f"HR>{self.heart_rate_max}, Temp>{self.temperature_max}, SpO2<{self.spo2_min}"
        )

    def get_thresholds(self) -> Dict[str, Any]:
        """
        Get current thresholds.

        Returns:
            Dictionary with current threshold values
        """
        return {
            "heart_rate_max": self.heart_rate_max,
            "temperature_max": self.temperature_max,
            "spo2_min": self.spo2_min,
        }
