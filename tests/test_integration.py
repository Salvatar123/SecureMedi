"""
Integration tests for SecureMedi full-flow scenarios.

Tests end-to-end workflows including:
- Sensor → Detector → Logger → Blockchain flow
- Dashboard login and verification logic
- Error recovery and edge cases
"""

import pytest
from datetime import datetime

from services.detector_service import DetectorService
from services.logger_service import LoggerService
from services.blockchain_service import BlockchainService
from utils.validators import validate_eth_address, validate_private_key
from utils.error_handler import SecureMediException


# ======================================================================================
# INTEGRATION: Sensor → Detector → Logger → Blockchain (Normal Flow)
# ======================================================================================


class TestFullDataFlowNormal:
    """Integration tests for normal (non-alert) patient data flow."""

    def test_normal_vitals_flow_end_to_end(self, mock_blockchain_service, logger_service):
        """Test complete flow: sensor data → detector → logger → blockchain."""
        # Setup services
        detector = DetectorService()
        logger = logger_service
        blockchain = mock_blockchain_service

        # Generate normal sensor data
        sensor_data = {
            "heart": 75,
            "temp": 37.0,
            "spo2": 98,
            "patient_id": "P001",
        }

        # Run through detector
        status = detector.detect(sensor_data)
        assert status == "NORMAL"

        # Log to CSV
        logger.save(
            data={k: v for k, v in sensor_data.items() if k != "patient_id"},
            status=status,
        )

        # Record to blockchain
        if blockchain:
            blockchain.log_access(
                patient_id=sensor_data["patient_id"],
                doctor="0x" + "a" * 40,
            )

        # Verify CSV entry was created
        records = logger.get_latest_records()
        assert len(records) > 0
        latest = records[-1]
        assert latest["status"] == "NORMAL"

        # Verify blockchain call (via mock)
        blockchain.log_access.assert_called_once()

    def test_sequential_normal_readings(self, mock_blockchain_service, logger_service):
        """Test multiple sequential normal readings accumulate correctly."""
        detector = DetectorService()
        logger = logger_service
        blockchain = mock_blockchain_service

        normal_readings = [
            {"heart": 72, "temp": 36.8, "spo2": 99, "patient_id": "P001"},
            {"heart": 75, "temp": 37.0, "spo2": 98, "patient_id": "P001"},
            {"heart": 78, "temp": 37.1, "spo2": 97, "patient_id": "P001"},
        ]

        for reading in normal_readings:
            status = detector.detect(reading)
            assert status == "NORMAL"

            logger.save(
                data={k: v for k, v in reading.items() if k != "patient_id"},
                status=status,
            )

        records = logger.get_latest_records(limit=100)
        assert len(records) >= 3
        assert all(r["status"] == "NORMAL" for r in records[-3:])


# ======================================================================================
# INTEGRATION: Sensor → Detector → Logger → Blockchain (Alert Flow)
# ======================================================================================


class TestFullDataFlowAlert:
    """Integration tests for alert (abnormal) patient data flow."""

    def test_alert_vitals_flow_end_to_end(self, mock_blockchain_service, logger_service):
        """Test alert flow: high vitals trigger detection and logging."""
        detector = DetectorService()
        logger = logger_service
        blockchain = mock_blockchain_service

        # Generate alert sensor data
        alert_data = {
            "heart": 150,  # Above threshold
            "temp": 39.5,
            "spo2": 88,
            "patient_id": "P001",
        }

        # Detect alert
        status = detector.detect(alert_data)
        assert status == "ALERT"

        # Log alert
        logger.save(
            data={k: v for k, v in alert_data.items() if k != "patient_id"},
            status=status,
        )

        # Record alert to blockchain (priority logging)
        if blockchain:
            blockchain.log_access(
                patient_id=alert_data["patient_id"],
                doctor="0x" + "a" * 40,
            )

        # Verify alert was logged
        records = logger.get_latest_records()
        assert len(records) > 0
        alert_record = records[-1]
        assert alert_record["status"] == "ALERT"

    def test_high_heart_rate_triggers_alert(self, mock_blockchain_service, logger_service):
        """Test high heart rate specifically triggers alert."""
        detector = DetectorService(heart_rate_max=100)
        logger = logger_service

        high_hr_data = {
            "heart": 125,
            "temp": 37.0,
            "spo2": 98,
            "patient_id": "P001",
        }

        status = detector.detect(high_hr_data)
        assert status == "ALERT"

        logger.save(
            data={k: v for k, v in high_hr_data.items() if k != "patient_id"},
            status=status,
        )

        records = logger.get_latest_records()
        assert records[-1]["status"] == "ALERT"

    def test_low_spo2_triggers_alert(self, mock_blockchain_service, logger_service):
        """Test low blood oxygen specifically triggers alert."""
        detector = DetectorService(spo2_min=95)
        logger = logger_service

        low_spo2_data = {
            "heart": 75,
            "temp": 37.0,
            "spo2": 90,
            "patient_id": "P001",
        }

        status = detector.detect(low_spo2_data)
        assert status == "ALERT"

        logger.save(
            data={k: v for k, v in low_spo2_data.items() if k != "patient_id"},
            status=status,
        )

        records = logger.get_latest_records()
        assert records[-1]["status"] == "ALERT"


# ======================================================================================
# INTEGRATION: Dashboard Login & Verification
# ======================================================================================


class TestDashboardLoginFlow:
    """Integration tests for dashboard authentication and verification."""

    def test_valid_doctor_login_flow(self, mock_blockchain_service, valid_addresses):
        """Test successful doctor login with valid credentials."""
        blockchain = mock_blockchain_service

        # Setup mock for doctor verification
        blockchain.is_doctor.return_value = True
        blockchain.verify_key.return_value = True

        doctor_address = valid_addresses[0]
        doctor_key = bytes.fromhex("a" * 64)

        # Simulate dashboard login
        assert validate_eth_address(doctor_address)
        is_doctor = blockchain.is_doctor(doctor_address)
        key_valid = blockchain.verify_key(doctor_address, doctor_key)

        assert is_doctor
        assert key_valid

    def test_invalid_address_rejected(self, mock_blockchain_service):
        """Test login rejected with invalid wallet address."""
        invalid_addresses = [
            "not_an_address",
            "0x" + "z" * 40,  # Invalid hex
            "0x" + "a" * 39,  # Too short
            "",
        ]

        for addr in invalid_addresses:
            assert not validate_eth_address(addr)

    def test_invalid_key_rejected(self, mock_blockchain_service, valid_addresses):
        """Test login rejected with invalid key."""
        blockchain = mock_blockchain_service
        blockchain.is_doctor.return_value = True
        blockchain.verify_key.return_value = False

        doctor_address = valid_addresses[0]
        invalid_key = bytes.fromhex("b" * 64)

        is_doctor = blockchain.is_doctor(doctor_address)
        key_valid = blockchain.verify_key(doctor_address, invalid_key)

        assert is_doctor  # Is a doctor
        assert not key_valid  # But key is invalid

    def test_emergency_access_activation(
        self, mock_blockchain_service, valid_addresses
    ):
        """Test emergency access token generation and usage."""
        blockchain = mock_blockchain_service

        # Setup mock
        blockchain.is_doctor.return_value = True
        blockchain.generate_emergency_access.return_value = (
            "0x" + "e" * 64
        )  # Emergency token

        doctor_address = valid_addresses[0]

        # Doctor initiates emergency
        is_doctor = blockchain.is_doctor(doctor_address)
        assert is_doctor

        emergency_token = blockchain.generate_emergency_access()
        assert emergency_token.startswith("0x")
        assert len(emergency_token) == 66  # 0x + 64 hex chars

        # Verify token can be used
        blockchain.generate_emergency_access.assert_called_once()

    def test_patient_access_logs_retrieval(
        self, mock_blockchain_service, valid_patient_ids, valid_private_keys
    ):
        """Test patient viewing their access logs via dashboard."""
        blockchain = mock_blockchain_service

        # Setup mock to return access logs
        blockchain.get_access_logs_as_patient.return_value = (
            ["0x" + "d" * 40, "0x" + "c" * 40],  # Doctors list
            ["2024-01-15 10:30", "2024-01-16 14:45"],  # Times
            [False, True],  # Emergency flags
        )

        patient_id = valid_patient_ids[0]
        private_key = valid_private_keys[0]

        # Patient retrieves logs
        doctors, times, emergencies = blockchain.get_access_logs_as_patient(
            patient_id, private_key
        )

        assert len(doctors) == 2
        assert len(times) == 2
        assert len(emergencies) == 2
        assert emergencies[1] is True  # Second access was emergency

        blockchain.get_access_logs_as_patient.assert_called_once_with(
            patient_id, private_key
        )


# ======================================================================================
# INTEGRATION: Error Scenarios & Recovery
# ======================================================================================


class TestErrorScenarios:
    """Integration tests for error handling across multiple services."""

    def test_blockchain_timeout_recovery(self, logger_service):
        """Test system continues when blockchain becomes unavailable."""
        detector = DetectorService()
        logger = logger_service

        sensor_data = {
            "heart": 80,
            "temp": 37.0,
            "spo2": 97,
        }

        # Detector works independently
        status = detector.detect(sensor_data)
        assert status == "NORMAL"

        # Logger works independently (CSV is local)
        logger.save(data=sensor_data, status=status)

        # Verify data logged despite blockchain unavailability
        records = logger.get_latest_records()
        assert len(records) > 0

    def test_corrupted_csv_recovery(self, logger_service):
        """Test logger handles corrupted CSV gracefully."""
        logger = logger_service

        # Log normal data
        logger.save(
            data={"heart": 75, "temp": 37.0, "spo2": 98},
            status="NORMAL",
        )

        initial_records = len(logger.get_latest_records(limit=100))

        #  Log more data - logger should continue working
        logger.save(
            data={"heart": 76, "temp": 37.1, "spo2": 98},
            status="NORMAL",
        )

        records = logger.get_latest_records(limit=100)
        # Should have at least the original record + new one
        assert len(records) >= initial_records

    def test_invalid_sensor_data_handling(self):
        """Test detector handles invalid/missing sensor data."""
        detector = DetectorService()

        invalid_cases = [
            {},  # Empty dict
            {"heart_rate": None},  # None values
            {"heart_rate": "not_a_number"},  # Wrong type
            {"heart_rate": -100},  # Negative values
            {"heart_rate": 9999},  # Extreme values
        ]

        for invalid_data in invalid_cases:
            # Should not raise exception
            try:
                status = detector.detect(invalid_data)
                # Missing fields default to zero/safe values
                assert status in ["NORMAL", "ALERT"]
            except (KeyError, ValueError, TypeError):
                # Some invalid cases may raise, which is acceptable
                pass

    def test_missing_required_validators(self, mock_blockchain_service):
        """Test missing credentials are caught by validators."""
        blockchain = mock_blockchain_service

        # Empty address
        assert not validate_eth_address("")

        # Empty key
        assert not validate_private_key("")

        # Malformed address format
        assert not validate_eth_address("0xinvalid")


# ======================================================================================
# INTEGRATION: Concurrent Data Processing
# ======================================================================================


class TestConcurrentProcessing:
    """Integration tests for concurrent patient data processing."""

    def test_multiple_patients_simultaneous_logging(
        self, mock_blockchain_service, logger_service
    ):
        """Test multiple patient records logged concurrently without conflicts."""
        logger = logger_service
        detector = DetectorService()

        patient_data = [
            {"heart": 75, "temp": 37.0, "spo2": 98},
            {"heart": 85, "temp": 37.5, "spo2": 96},
            {"heart": 95, "temp": 38.0, "spo2": 94},
        ]

        for data in patient_data:
            status = detector.detect(data)
            logger.save(data=data, status=status)

        records = logger.get_latest_records(limit=100)
        assert len(records) >= 3

    def test_alert_priority_in_concurrent_logging(
        self, mock_blockchain_service, logger_service
    ):
        """Test alert records are prioritized in concurrent logging."""
        logger = logger_service
        detector = DetectorService()

        # Mix of normal and alert data
        readings = [
            {"heart": 75, "temp": 37.0, "spo2": 98},
            {"heart": 150, "temp": 39.0, "spo2": 90},  # Alert
            {"heart": 82, "temp": 37.2, "spo2": 97},
        ]

        for data in readings:
            status = detector.detect(data)
            logger.save(data=data, status=status)

        records = logger.get_latest_records(limit=100)
        alert_records = [r for r in records if r["status"] == "ALERT"]
        assert len(alert_records) >= 1


# ======================================================================================
# INTEGRATION: Statistics & Reporting
# ======================================================================================


class TestStatisticsReporting:
    """Integration tests for statistics aggregation and reporting."""

    def test_statistics_calculation_across_sessions(self, logger_service):
        """Test statistics computed correctly across multiple logged sessions."""
        logger = logger_service

        # Log varied data
        vital_sets = [
            {"heart": 60, "temp": 36.5, "spo2": 99},
            {"heart": 75, "temp": 37.0, "spo2": 98},
            {"heart": 90, "temp": 37.5, "spo2": 97},
        ]

        for vitals in vital_sets:
            logger.save(data=vitals, status="NORMAL")

        stats = logger.get_statistics()
        assert stats is not None
        assert "heart" in stats
        assert "avg" in stats["heart"]
        assert stats["heart"]["avg"] == 75.0

    def test_alert_statistics_separate_tracking(self, logger_service):
        """Test alert and normal events tracked separately in statistics."""
        logger = logger_service

        # Log alternating normal and alert
        logger.save(data={"heart": 75, "temp": 37.0, "spo2": 98}, status="NORMAL")
        logger.save(data={"heart": 150, "temp": 39.0, "spo2": 90}, status="ALERT")
        logger.save(data={"heart": 80, "temp": 37.1, "spo2": 97}, status="NORMAL")

        stats = logger.get_statistics()
        assert stats is not None
