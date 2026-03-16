"""
Input validators for the application.
Ensures data integrity and security.
"""

import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)


def validate_eth_address(address: str) -> bool:
    """
    Validate Ethereum wallet address format.

    Args:
        address: Address to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(address, str):
        return False

    if not address.startswith("0x"):
        return False

    if len(address) != 42:
        return False

    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def validate_private_key(key: str) -> bool:
    """
    Validate Ethereum private key format.

    Args:
        key: Private key to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(key, str):
        return False

    if not key.startswith("0x"):
        return False

    if len(key) != 66:
        return False

    try:
        int(key, 16)
        return True
    except ValueError:
        return False


def validate_patient_id(patient_id: str) -> bool:
    """
    Validate patient ID format.

    Args:
        patient_id: Patient ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(patient_id, str):
        return False

    if not re.match(r"^P\d{3,}$", patient_id):
        return False

    return True


def validate_health_data(data: Dict[str, Any]) -> bool:
    """
    Validate health vital signs data.

    Args:
        data: Dictionary with heart, temp, spo2

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False

    required_keys = {"heart", "temp", "spo2"}
    if not required_keys.issubset(data.keys()):
        return False

    try:
        heart = int(data["heart"])
        temp = float(data["temp"])
        spo2 = int(data["spo2"])

        if not (30 <= heart <= 200):
            logger.warning(f"Heart rate out of range: {heart}")
            return False

        if not (32 <= temp <= 42):
            logger.warning(f"Temperature out of range: {temp}")
            return False

        if not (0 <= spo2 <= 100):
            logger.warning(f"SpO2 out of range: {spo2}")
            return False

        return True

    except (ValueError, TypeError) as e:
        logger.error(f"Invalid health data format: {e}")
        return False


def validate_status(status: str) -> bool:
    """
    Validate alert status.

    Args:
        status: Status to validate (ALERT or NORMAL)

    Returns:
        True if valid, False otherwise
    """
    return status in ("ALERT", "NORMAL")
