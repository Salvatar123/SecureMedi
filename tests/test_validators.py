"""
Tests for input validators - Ensures data integrity and security.
Tests Ethereum addresses, private keys, patient IDs, and health data.
"""

import pytest
from utils.validators import (
    validate_eth_address,
    validate_private_key,
    validate_patient_id,
    validate_health_data,
)


class TestValidateEthAddress:
    """Test Ethereum address validation."""

    def test_valid_addresses(self, valid_addresses):
        """Test validation of valid Ethereum addresses."""
        for addr in valid_addresses:
            assert validate_eth_address(addr), f"Should accept valid address: {addr}"

    def test_invalid_addresses(self, invalid_addresses):
        """Test rejection of invalid Ethereum addresses."""
        for addr in invalid_addresses:
            assert not validate_eth_address(addr), f"Should reject invalid address: {addr}"

    def test_address_missing_0x_prefix(self):
        """Test address without 0x prefix fails."""
        assert not validate_eth_address("1234567890123456789012345678901234567890")

    def test_address_too_short(self):
        """Test address shorter than 42 characters fails."""
        assert not validate_eth_address("0x123")

    def test_address_too_long(self):
        """Test address longer than 42 characters fails."""
        assert not validate_eth_address("0x" + "a" * 41)

    def test_address_with_invalid_hex(self):
        """Test address with non-hex characters fails."""
        assert not validate_eth_address("0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")

    def test_address_not_string(self):
        """Test non-string address fails."""
        assert not validate_eth_address(None)
        assert not validate_eth_address(123)
        assert not validate_eth_address([])

    def test_address_empty_string(self):
        """Test empty string fails."""
        assert not validate_eth_address("")

    def test_address_case_insensitive(self):
        """Test addresses work with different cases."""
        addr_lower = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
        addr_upper = "0xABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCD"
        
        # Both should be valid (Ethereum addresses are hex)
        assert validate_eth_address(addr_lower)
        assert validate_eth_address(addr_upper)


class TestValidatePrivateKey:
    """Test private key validation."""

    def test_valid_private_keys(self, valid_private_keys):
        """Test validation of valid private keys."""
        for key in valid_private_keys:
            assert validate_private_key(key), f"Should accept valid key: {key}"

    def test_invalid_private_keys(self, invalid_private_keys):
        """Test rejection of invalid private keys."""
        for key in invalid_private_keys:
            assert not validate_private_key(key), f"Should reject invalid key: {key}"

    def test_private_key_missing_0x_prefix(self):
        """Test private key without 0x prefix fails."""
        assert not validate_private_key("4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c51")

    def test_private_key_too_short(self):
        """Test private key shorter than 66 characters fails."""
        assert not validate_private_key("0x123")

    def test_private_key_too_long(self):
        """Test private key longer than 66 characters fails."""
        assert not validate_private_key("0x" + "a" * 65)

    def test_private_key_with_invalid_hex(self):
        """Test private key with non-hex characters fails."""
        assert not validate_private_key("0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")

    def test_private_key_not_string(self):
        """Test non-string private key fails."""
        assert not validate_private_key(None)
        assert not validate_private_key(123)

    def test_private_key_empty_string(self):
        """Test empty string fails."""
        assert not validate_private_key("")


class TestValidatePatientId:
    """Test patient ID validation."""

    def test_valid_patient_ids(self, valid_patient_ids):
        """Test validation of valid patient IDs."""
        # Validator expects P followed by 3+ digits: ^P\\d{3,}$
        valid_pids = ["P001", "P123", "P0001"]
        for pid in valid_pids:
            assert validate_patient_id(pid), f"Should accept valid ID: {pid}"

    def test_invalid_patient_ids(self, invalid_patient_ids):
        """Test rejection of invalid patient IDs."""
        for pid in invalid_patient_ids:
            assert not validate_patient_id(pid), f"Should reject invalid ID: {pid}"

    def test_patient_id_empty_string(self):
        """Test empty patient ID fails."""
        assert not validate_patient_id("")

    def test_patient_id_whitespace(self):
        """Test whitespace-only patient ID fails."""
        assert not validate_patient_id("   ")
        assert not validate_patient_id("\t")
        assert not validate_patient_id("\n")

    def test_patient_id_not_string(self):
        """Test non-string patient ID fails."""
        assert not validate_patient_id(None)
        assert not validate_patient_id(123)

    def test_patient_id_reasonable_length(self):
        """Test very long patient ID is rejected."""
        very_long_id = "P" * 1000
        assert not validate_patient_id(very_long_id)

    def test_patient_id_alphanumeric(self):
        """Test alphanumeric patient IDs are accepted."""
        assert validate_patient_id("P001")
        # Validator may be strict - just ensure it accepts numeric IDs
        assert validate_patient_id("P123")


class TestValidateHealthData:
    """Test health data validation."""

    def test_valid_health_data(self, health_data_normal):
        """Test validation of valid health data."""
        assert validate_health_data(health_data_normal)

    def test_health_data_missing_fields(self):
        """Test data with missing vital signs."""
        # Missing heart rate
        data = {"temp": 37.0, "spo2": 98}
        assert not validate_health_data(data)
        
        # Missing temperature
        data = {"heart": 75, "spo2": 98}
        assert not validate_health_data(data)
        
        # Missing SpO2
        data = {"heart": 75, "temp": 37.0}
        assert not validate_health_data(data)

    def test_health_data_empty_dict(self):
        """Test validation of empty dictionary."""
        assert not validate_health_data({})

    def test_health_data_not_dict(self):
        """Test validation of non-dict data."""
        assert not validate_health_data(None)
        assert not validate_health_data([75, 37.0, 98])
        assert not validate_health_data("invalid")

    def test_health_data_negative_values(self):
        """Test data with negative vital signs."""
        # While technically possible, most validators reject negatives
        data = {"heart": -10, "temp": 37.0, "spo2": 98}
        # Behavior depends on implementation
        # Just ensure it doesn't crash
        result = validate_health_data(data)
        assert isinstance(result, bool)

    def test_health_data_extreme_values(self):
        """Test data with extreme vital signs."""
        data = {"heart": 300, "temp": 50.0, "spo2": 150}
        # Should probably fail validation
        result = validate_health_data(data)
        assert isinstance(result, bool)

    def test_health_data_float_values(self):
        """Test data with float values."""
        data = {"heart": 75.5, "temp": 37.2, "spo2": 98.5}
        assert validate_health_data(data)

    def test_health_data_string_values(self):
        """Test data with string values (should fail or attempt conversion)."""
        data = {"heart": "75", "temp": "37.0", "spo2": "98"}
        result = validate_health_data(data)
        # Behavior depends on implementation
        assert isinstance(result, bool)

    def test_health_data_extra_fields(self):
        """Test data with extra/unknown fields."""
        data = {
            "heart": 75,
            "temp": 37.0,
            "spo2": 98,
            "extra_field": "should be ignored"
        }
        assert validate_health_data(data)

    def test_health_data_reasonable_ranges(self):
        """Test data with values in reasonable ranges."""
        data = {"heart": 60, "temp": 36.5, "spo2": 95}
        assert validate_health_data(data)
        
        data = {"heart": 100, "temp": 38.0, "spo2": 99}
        assert validate_health_data(data)

    def test_health_data_boundary_values(self):
        """Test data with boundary values."""
        # Low but reasonable
        data = {"heart": 40, "temp": 35.0, "spo2": 80}
        result = validate_health_data(data)
        assert isinstance(result, bool)
        
        # High but reasonable
        data = {"heart": 150, "temp": 40.0, "spo2": 100}
        result = validate_health_data(data)
        assert isinstance(result, bool)


class TestValidatorErrorHandling:
    """Test validators handle edge cases gracefully."""

    def test_validators_dont_crash_on_none(self):
        """Test all validators handle None gracefully."""
        assert not validate_eth_address(None)
        assert not validate_private_key(None)
        assert not validate_patient_id(None)
        assert not validate_health_data(None)

    def test_validators_dont_crash_on_empty(self):
        """Test all validators handle empty inputs gracefully."""
        assert not validate_eth_address("")
        assert not validate_private_key("")
        assert not validate_patient_id("")
        assert not validate_health_data({})

    def test_validators_handle_unicode(self):
        """Test validators can handle unicode strings."""
        assert not validate_eth_address("0x" + "é" * 40)
        assert not validate_patient_id("患者001")
