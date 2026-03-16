"""
Tests for BlockchainService - Web3 interactions and smart contract calls.
Uses mocks to avoid requiring actual blockchain node.
"""

import pytest
from unittest.mock import patch, MagicMock
from services.blockchain_service import BlockchainService


class TestBlockchainServiceInitialization:
    """Test blockchain service initialization."""

    @patch("services.blockchain_service.Web3")
    def test_initialization_success(self, mock_web3_class, mock_web3):
        """Test successful blockchain initialization."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            # Mock file reading
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                assert service.w3 is not None
                assert service.account is not None
                assert service.contract is not None

    @patch("services.blockchain_service.Web3")
    def test_initialization_connection_error(self, mock_web3_class, mock_web3):
        """Test initialization fails when blockchain is unreachable."""
        mock_web3.is_connected.return_value = False
        mock_web3_class.return_value = mock_web3

        with pytest.raises(ConnectionError):
            BlockchainService()

    @patch("services.blockchain_service.Web3")
    def test_initialization_missing_abi_file(self, mock_web3_class, mock_web3):
        """Test initialization fails when ABI file is missing."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                BlockchainService()


class TestBlockchainServiceKeyGeneration:
    """Test key generation operations."""

    @patch("services.blockchain_service.Web3")
    def test_generate_key(self, mock_web3_class, mock_web3):
        """Test key generation transaction."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                # Mock contract function
                mock_contract = MagicMock()
                service.contract = mock_contract

                service.generate_key()

                # Verify transaction was initiated
                mock_contract.functions.generateKey.assert_called_once()

    @patch("services.blockchain_service.Web3")
    def test_get_my_key(self, mock_web3_class, mock_web3):
        """Test retrieving access key."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.getMyKey.return_value.call.return_value = b"test_key"
                service.contract = mock_contract

                key = service.get_my_key()

                assert key == b"test_key"


class TestBlockchainServiceAccessVerification:
    """Test key verification operations."""

    @patch("services.blockchain_service.Web3")
    def test_verify_key_valid(self, mock_web3_class, mock_web3):
        """Test verifying a valid key."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.verifyKey.return_value.call.return_value = True
                service.contract = mock_contract

                user = "0x1234567890123456789012345678901234567890"
                key = b"valid_key"

                result = service.verify_key(user, key)

                assert result is True

    @patch("services.blockchain_service.Web3")
    def test_verify_key_invalid(self, mock_web3_class, mock_web3):
        """Test verifying an invalid key."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.verifyKey.return_value.call.return_value = False
                service.contract = mock_contract

                user = "0x1234567890123456789012345678901234567890"
                key = b"invalid_key"

                result = service.verify_key(user, key)

                assert result is False


class TestBlockchainServiceAccessLogging:
    """Test access logging operations."""

    @patch("services.blockchain_service.Web3")
    def test_log_access(self, mock_web3_class, mock_web3):
        """Test logging patient access."""
        mock_web3_class.return_value = mock_web3
        mock_web3.eth.account.sign_transaction.return_value = MagicMock(
            raw_transaction=b"signed_tx"
        )
        mock_web3.eth.send_raw_transaction.return_value = b"tx_hash_123"

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                service.contract = mock_contract

                tx_hash = service.log_access("P001")

                assert tx_hash is not None
                assert mock_web3.eth.wait_for_transaction_receipt.called


class TestBlockchainServiceDoctorRegistration:
    """Test doctor registration operations."""

    @patch("services.blockchain_service.Web3")
    def test_register_doctor(self, mock_web3_class, mock_web3):
        """Test registering a doctor."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                service.contract = mock_contract

                wallet = "0x1234567890123456789012345678901234567890"
                service.register_doctor(wallet)

                mock_contract.functions.registerDoctor.assert_called_with(wallet)

    @patch("services.blockchain_service.Web3")
    def test_is_doctor_true(self, mock_web3_class, mock_web3):
        """Test checking if address is a registered doctor."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.isDoctor.return_value.call.return_value = True
                service.contract = mock_contract

                address = "0x1234567890123456789012345678901234567890"
                result = service.is_doctor(address)

                assert result is True

    @patch("services.blockchain_service.Web3")
    def test_is_doctor_false(self, mock_web3_class, mock_web3):
        """Test checking non-doctor address."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.isDoctor.return_value.call.return_value = False
                service.contract = mock_contract

                address = "0x0000000000000000000000000000000000000000"
                result = service.is_doctor(address)

                assert result is False


class TestBlockchainServicePatientRegistration:
    """Test patient registration operations."""

    @patch("services.blockchain_service.Web3")
    def test_register_patient(self, mock_web3_class, mock_web3):
        """Test registering a patient."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                service.contract = mock_contract

                patient_id = "P001"
                wallet = "0x1234567890123456789012345678901234567890"
                service.register_patient(patient_id, wallet)

                mock_contract.functions.registerPatient.assert_called_with(patient_id, wallet)


class TestBlockchainServiceAccessLogs:
    """Test access log retrieval."""

    @patch("services.blockchain_service.Web3")
    def test_get_access_logs(self, mock_web3_class, mock_web3):
        """Test retrieving access logs for a patient."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_doctors = ["0xdoc1", "0xdoc2"]
                mock_times = [1000, 2000]
                mock_emergencies = [False, True]

                mock_contract.functions.getAccessLogs.return_value.call.return_value = (
                    mock_doctors,
                    mock_times,
                    mock_emergencies,
                )
                service.contract = mock_contract

                doctors, times, emergencies = service.get_access_logs("P001")

                assert doctors == mock_doctors
                assert times == mock_times
                assert emergencies == mock_emergencies

    @patch("services.blockchain_service.Web3")
    def test_get_access_logs_as_patient(self, mock_web3_class, mock_web3):
        """Test patient retrieving their own access logs."""
        mock_web3_class.return_value = mock_web3
        mock_web3.eth.account.from_key.return_value = MagicMock(address="0xpatient_addr")

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.getAccessLogs.return_value.call.return_value = (
                    ["0xdoc1"],
                    [1000],
                    [False],
                )
                service.contract = mock_contract

                patient_id = "P001"
                private_key = "0x4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c51"

                doctors, times, emergencies = service.get_access_logs_as_patient(
                    patient_id, private_key
                )

                assert len(doctors) == 1


class TestBlockchainServiceEmergencyAccess:
    """Test emergency access operations."""

    @patch("services.blockchain_service.Web3")
    def test_generate_emergency_access(self, mock_web3_class, mock_web3):
        """Test generating emergency access token."""
        mock_web3_class.return_value = mock_web3
        mock_web3.eth.account.sign_transaction.return_value = MagicMock(
            raw_transaction=b"signed_tx"
        )
        mock_web3.eth.send_raw_transaction.return_value = b"emergency_token"

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                service.contract = mock_contract

                token = service.generate_emergency_access()

                assert token is not None


class TestBlockchainServiceErrorHandling:
    """Test error handling in blockchain service."""

    @patch("services.blockchain_service.Web3")
    def test_error_on_failed_transaction(self, mock_web3_class, mock_web3):
        """Test error handling for failed transactions."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.generateKey.side_effect = Exception("Transaction failed")
                service.contract = mock_contract

                with pytest.raises(Exception):
                    service.generate_key()

    @patch("services.blockchain_service.Web3")
    def test_error_on_invalid_address(self, mock_web3_class, mock_web3):
        """Test error handling for invalid addresses."""
        mock_web3_class.return_value = mock_web3

        with patch("builtins.open", create=True):
            with patch("json.load", return_value=[]):
                service = BlockchainService()

                mock_contract = MagicMock()
                mock_contract.functions.isDoctor.side_effect = ValueError("Invalid address")
                service.contract = mock_contract

                with pytest.raises(ValueError):
                    service.is_doctor("invalid_address")
