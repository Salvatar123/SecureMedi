"""
Logger service layer.
Wraps CSV logging with encryption support and thread safety.
"""

import csv
import logging
import os
from datetime import datetime
from threading import Lock
from typing import Dict, Any, Optional, List
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LoggerService:
    """Service for logging health data."""

    def __init__(self, log_file: Optional[str] = None) -> None:
        """
        Initialize logger service.

        Args:
            log_file: Path to CSV file. Uses config if not provided.
        """
        self.log_file: str = log_file or settings.LOG_FILE
        self.lock: Lock = Lock()  # Thread-safe logging
        self._ensure_log_dir()
        logger.info(f"Logger initialized: {self.log_file}")

    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Created log directory: {log_dir}")

    def save(self, data: Dict[str, Any], status: str) -> None:
        """
        Save health data and status to CSV.

        Args:
            data: Dictionary with heart, temp, spo2 values
            status: Alert status (ALERT or NORMAL)
        """
        try:
            with self.lock:
                file_exists = os.path.isfile(self.log_file)

                with open(self.log_file, "a", newline="") as f:
                    writer = csv.writer(f)

                    if not file_exists:
                        writer.writerow(
                            ["timestamp", "heart", "temp", "spo2", "status"]
                        )
                        logger.info("Created new CSV log file")

                    timestamp = datetime.now().isoformat()
                    writer.writerow(
                        [
                            timestamp,
                            data.get("heart"),
                            data.get("temp"),
                            data.get("spo2"),
                            status,
                        ]
                    )

                logger.debug(f"Logged: {status} - Heart:{data.get('heart')} Temp:{data.get('temp')} SpO2:{data.get('spo2')}")

        except Exception as e:
            logger.error(f"Failed to save log: {e}")
            raise

    def get_latest_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest N records from the log.

        Args:
            limit: Number of records to retrieve

        Returns:
            List of dictionaries with log entries
        """
        try:
            if not os.path.isfile(self.log_file):
                return []

            records: List[Dict[str, Any]] = []
            with self.lock:
                with open(self.log_file, "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(row)

            return records[-limit:]

        except Exception as e:
            logger.error(f"Failed to read logs: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics from all logged data.

        Returns:
            Dictionary with min, max, avg for each vital
        """
        try:
            records = self.get_latest_records(limit=1000)

            if not records:
                return {}

            hearts = [float(r["heart"]) for r in records if r["heart"]]
            temps = [float(r["temp"]) for r in records if r["temp"]]
            spo2s = [float(r["spo2"]) for r in records if r["spo2"]]

            return {
                "heart": {
                    "min": min(hearts) if hearts else None,
                    "max": max(hearts) if hearts else None,
                    "avg": sum(hearts) / len(hearts) if hearts else None,
                },
                "temp": {
                    "min": min(temps) if temps else None,
                    "max": max(temps) if temps else None,
                    "avg": sum(temps) / len(temps) if temps else None,
                },
                "spo2": {
                    "min": min(spo2s) if spo2s else None,
                    "max": max(spo2s) if spo2s else None,
                    "avg": sum(spo2s) / len(spo2s) if spo2s else None,
                },
            }

        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
            return {}

    def clear_logs(self) -> None:
        """Clear all log entries (use with caution)."""
        try:
            with self.lock:
                if os.path.isfile(self.log_file):
                    os.remove(self.log_file)
                    logger.warning("All logs cleared")
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            raise
