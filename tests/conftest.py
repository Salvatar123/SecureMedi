"""
Pytest configuration and fixtures for SecureMedi tests.
Provides mocks for blockchain, logger, sensor, and detector services.
"""

import pytest
import os
from unittest.mock import MagicMock, patch

# Import services for fixtures
from services.logger_service import LoggerService
from services.detector_service import DetectorService
from config.settings import get_settings

# ================================================================
# SESSION FIXTURES (run once per test session)
# ================================================================


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings."""
    with patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "testing",
            "GANACHE_URL": "http://127.0.0.1:7545",
            "CONTRACT_ADDRESS": "0x9feb5BA604B3C467Cd07Ecd20a9d8d601a2D98Fd",
            "PRIVATE_KEY": "0x4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c51",
            "ENABLE_BLOCKCHAIN": "false",
            "ENABLE_LOCAL_LOGGING": "true",
            "LOG_FILE": "logs/test_data.csv",
        },
    ):
        yield get_settings()


# ================================================================
# DETECTOR SERVICE FIXTURES
# ================================================================


@pytest.fixture
def detector_service():
    """Create a detector service for testing."""
    return DetectorService(heart_rate_max=110, temperature_max=38.0, spo2_min=92)


@pytest.fixture
def health_data_normal():
    """Generate normal health data."""
    return {"heart": 75, "temp": 37.2, "spo2": 98}


@pytest.fixture
def health_data_alert_high_heart():
    """Generate health data with elevated heart rate (ALERT)."""
    return {"heart": 115, "temp": 37.0, "spo2": 98}


@pytest.fixture
def health_data_alert_high_temp():
    """Generate health data with elevated temperature (ALERT)."""
    return {"heart": 75, "temp": 38.5, "spo2": 98}


@pytest.fixture
def health_data_alert_low_spo2():
    """Generate health data with low SpO2 (ALERT)."""
    return {"heart": 75, "temp": 37.0, "spo2": 90}


# ================================================================
# LOGGER SERVICE FIXTURES
# ================================================================


@pytest.fixture
def logger_service(tmp_path):
    """Create a logger service with temporary log file."""
    log_file = tmp_path / "test_logs.csv"
    return LoggerService(log_file=str(log_file))


# ================================================================
# BLOCKCHAIN SERVICE MOCKS
# ================================================================


@pytest.fixture
def mock_blockchain_service():
    """Create a mock blockchain service."""
    mock_service = MagicMock()

    # Mock methods
    mock_service.generate_key = MagicMock(return_value=None)
    mock_service.get_my_key = MagicMock(return_value=b"test_key_123")
    mock_service.verify_key = MagicMock(return_value=True)
    mock_service.log_access = MagicMock(return_value="0xabc123")
    mock_service.register_doctor = MagicMock(return_value=None)
    mock_service.is_doctor = MagicMock(return_value=True)
    mock_service.register_patient = MagicMock(return_value=None)
    mock_service.get_access_logs = MagicMock(
        return_value=(["0xdoc1", "0xdoc2"], [1000, 2000], [False, True])
    )
    mock_service.generate_emergency_access = MagicMock(return_value="0xemerg_token")

    return mock_service


@pytest.fixture
def mock_web3():
    """Create a mock Web3 connection."""
    mock = MagicMock()

    # Mock connection status
    mock.is_connected = MagicMock(return_value=True)

    # Mock eth methods
    mock.eth.accounts = ["0x1234567890123456789012345678901234567890"]
    mock.eth.get_balance = MagicMock(return_value=1000000000000000000)
    mock.eth.get_transaction_count = MagicMock(return_value=0)
    mock.eth.wait_for_transaction_receipt = MagicMock(return_value={"transactionHash": b"0xabc123"})
    mock.eth.send_raw_transaction = MagicMock(return_value=b"0xtx_hash")

    # Mock conversion methods
    mock.from_wei = MagicMock(return_value=1.0)
    mock.to_wei = MagicMock(return_value=1000000000000000000)

    # Mock contract
    mock.eth.contract = MagicMock(return_value=MagicMock())

    # Mock account
    mock.eth.account.sign_transaction = MagicMock(
        return_value=MagicMock(raw_transaction=b"signed_tx")
    )
    mock.eth.account.from_key = MagicMock(
        return_value=MagicMock(address="0x1234567890123456789012345678901234567890")
    )

    return mock


# ================================================================
# SENSOR DATA FIXTURES
# ================================================================


@pytest.fixture
def sensor_data_generator():
    """Generate random sensor data."""

    def _generate(heart_rate=75, temperature=37.2, spo2=98, variance=True):
        import random

        if variance:
            return {
                "heart": heart_rate + random.randint(-5, 5),
                "temp": temperature + random.uniform(-0.5, 0.5),
                "spo2": spo2 + random.randint(-2, 2),
            }
        return {"heart": heart_rate, "temp": temperature, "spo2": spo2}

    return _generate


# ================================================================
# VALIDATOR TEST DATA
# ================================================================


@pytest.fixture
def valid_addresses():
    """Collection of valid Ethereum addresses."""
    return [
        "0x1234567890123456789012345678901234567890",
        "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        "0x0000000000000000000000000000000000000000",
    ]


@pytest.fixture
def invalid_addresses():
    """Collection of invalid Ethereum addresses."""
    return [
        "1234567890123456789012345678901234567890",  # Missing 0x
        "0x123456789012345678901234567890123456789",  # Too short
        "0x12345678901234567890123456789012345678901",  # Too long
        "0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",  # Invalid hex chars
        "invalid",
        "",
    ]


@pytest.fixture
def valid_private_keys():
    """Collection of valid private keys."""
    return [
        "0x4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c51",
        "0x0000000000000000000000000000000000000000000000000000000000000001",
    ]


@pytest.fixture
def invalid_private_keys():
    """Collection of invalid private keys."""
    return [
        "4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c51",  # Missing 0x
        "0x4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c5",  # Too short
        "0x4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c511",  # Too long
        "0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",  # Invalid hex
        "",
    ]


@pytest.fixture
def valid_patient_ids():
    """Collection of valid patient IDs."""
    return ["P001", "P123", "PATIENT001", "P-001"]


@pytest.fixture
def invalid_patient_ids():
    """Collection of invalid patient IDs."""
    return ["", " ", "P" * 100]  # Empty, whitespace, too long


# ================================================================
# AUTOUSE FIXTURES (run for every test)
# ================================================================


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment between tests."""
    yield
    # Cleanup after each test
    import glob

    for f in glob.glob("logs/test_*.csv"):
        try:
            os.remove(f)
        except OSError:
            pass
