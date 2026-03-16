import time
import logging
import signal
import sys
from typing import Optional, Dict, Any

# Configuration
from config.settings import get_settings, Settings

# Services
from services.detector_service import DetectorService
from services.logger_service import LoggerService
from services.blockchain_service import BlockchainService

# Utilities
from edge_ai.sensor import generate_data
from utils.validators import validate_health_data

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SecureMediSystem:
    """Main SecureMedi monitoring system."""

    def __init__(self) -> None:
        """Initialize system components."""
        self.settings: Settings = get_settings()
        self.logger_service: LoggerService = LoggerService()
        self.detector_service: DetectorService = DetectorService()
        self.blockchain_service: Optional[BlockchainService] = None

        if self.settings.ENABLE_BLOCKCHAIN:
            try:
                self.blockchain_service = BlockchainService()
            except Exception as e:
                logger.warning(f"Blockchain disabled: {e}")
                self.blockchain_service = None

        self.running: bool = True
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        logger.info("Shutdown signal received")
        self.running = False
        sys.exit(0)

    def run(self) -> None:
        """Main monitoring loop."""
        logger.info("🚀 secureMedi System Started...")

        try:
            while self.running:
                # 1. Generate sensor data
                data: Dict[str, Any] = generate_data()

                # 2. Validate data
                if not validate_health_data(data):
                    logger.warning(f"Invalid health data: {data}")
                    continue

                # 3. Detect anomaly
                status: str = self.detector_service.detect(data)

                # 4. Print output
                logger.info(f"Vitals: {data}")
                logger.info(f"Status: {status}")

                # 5. Save locally
                if self.settings.ENABLE_LOCAL_LOGGING:
                    try:
                        self.logger_service.save(data, status)
                    except Exception as e:
                        logger.error(f"Failed to save logs: {e}")

                # 6. Send ALERT to blockchain
                if status == "ALERT" and self.blockchain_service:
                    try:
                        patient_id = self.settings.DEFAULT_PATIENT_ID
                        tx_hash = self.blockchain_service.log_access(patient_id)
                        logger.info(f"✅ Alert stored on Blockchain: {tx_hash}")
                    except Exception as e:
                        logger.error(f"❌ Blockchain Error: {e}")

                logger.info("-" * 40)
                time.sleep(self.settings.SENSOR_INTERVAL_SEC)

        except KeyboardInterrupt:
            logger.info("System interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            logger.info("🛑 System shutdown complete")


def main():
    """Entry point."""
    system = SecureMediSystem()
    system.run()


if __name__ == "__main__":
    main()
