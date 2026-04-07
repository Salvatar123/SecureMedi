"""Health Service - Wraps existing health monitoring services"""

import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from services.logger_service import LoggerService
from services.detector_service import DetectorService
from app.models.health import HealthData, Alert, HealthStatus

logger = logging.getLogger(__name__)


class HealthService:
    """Service for health data operations"""
    
    def __init__(self):
        """Initialize services"""
        try:
            self.logger_service = LoggerService()
            self.detector_service = DetectorService()
        except Exception as e:
            logger.warning(f"Could not initialize services: {e}")
            self.logger_service = None
            self.detector_service = None
    
    def get_latest_health_data(self, limit: int = 100) -> List[HealthData]:
        """Get latest health records"""
        try:
            if not self.logger_service:
                return []
            
            records = self.logger_service.get_latest_records(limit)
            
            health_data = []
            for record in records:
                try:
                    hd = HealthData(
                        heart_rate=int(record.get("heart", 0)),
                        temperature=float(record.get("temp", 0)),
                        spo2=int(record.get("spo2", 0)),
                        timestamp=record.get("timestamp", datetime.now()),
                        status=HealthStatus(record.get("status", "NORMAL"))
                    )
                    health_data.append(hd)
                except Exception as e:
                    logger.debug(f"Could not parse record: {e}")
            
            return health_data
        except Exception as e:
            logger.error(f"Error getting health data: {e}")
            return []
    
    def get_health_statistics(self) -> Dict[str, Any]:
        """Get health statistics"""
        try:
            if not self.logger_service:
                return {}
            
            return self.logger_service.get_statistics()
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_alerts(self, patient_id: Optional[str] = None) -> List[Alert]:
        """Get active alerts"""
        # This would connect to blockchain to get stored alerts
        try:
            # For now, return empty list - can be extended with blockchain queries
            return []
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def log_health_data(self, data: HealthData) -> bool:
        """Log new health data"""
        try:
            if not self.logger_service:
                return False
            
            record = {
                "heart": data.heart_rate,
                "temp": data.temperature,
                "spo2": data.spo2,
                "status": data.status
            }
            self.logger_service.save(record, data.status)
            return True
        except Exception as e:
            logger.error(f"Error logging health data: {e}")
            return False
