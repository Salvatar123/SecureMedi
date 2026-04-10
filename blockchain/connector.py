"""
Backward compatibility wrapper for blockchain operations.
This module maintains backward compatibility with legacy code
that used to import directly from blockchain.connector.
Now it delegates to the service layer.
"""

from typing import Optional, Tuple
from services.blockchain_service import BlockchainService


class BlockchainConnector:
    """Connector class for blockchain operations - wraps BlockchainService."""
    
    def __init__(self):
        """Initialize connector."""
        self._service = BlockchainService()
    
    def generate_key(self) -> None:
        """Generate a new access key."""
        return self._service.generate_key()
    
    def get_my_key(self) -> bytes:
        """Get the access key for current account."""
        return self._service.get_my_key()
    
    def verify_key(self, user: str, key: bytes) -> bool:
        """Verify if a user has a valid access key."""
        return self._service.verify_key(user, key)
    
    def log_access(self, patient_id: str) -> str:
        """Log patient access on blockchain."""
        return self._service.log_access(patient_id)
    
    def register_doctor(self, wallet: str) -> None:
        """Register a doctor wallet."""
        return self._service.register_doctor(wallet)
    
    def is_doctor(self, address: str) -> bool:
        """Check if an address is a registered doctor."""
        return self._service.is_doctor(address)
    
    def register_patient(self, patient_id: str, wallet: str) -> None:
        """Register a patient with their wallet."""
        return self._service.register_patient(patient_id, wallet)

    def is_patient(self, patient_id: str) -> bool:
        """Check if a patient ID is registered."""
        return self._service.is_patient(patient_id)
    
    def get_access_logs(self, patient_id: str) -> Tuple[list, list, list]:
        """Get access logs for a patient."""
        return self._service.get_access_logs(patient_id)
    
    def get_access_logs_as_patient(self, patient_id: str, private_key: str) -> Tuple[list, list, list]:
        """Get access logs as a patient using their private key."""
        return self._service.get_access_logs_as_patient(patient_id, private_key)
    
    def generate_emergency_access(self) -> str:
        """Generate an emergency access token."""
        return self._service.generate_emergency_access()


# Create singleton instance for backward compatibility
_service_instance: Optional[BlockchainService] = None


def _get_service() -> BlockchainService:
    """Get or create blockchain service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = BlockchainService()
    return _service_instance


# Expose service methods at module level
def generate_key() -> None:
    """Generate a new access key. (Backward compat wrapper)"""
    return _get_service().generate_key()


def get_my_key() -> bytes:
    """Get the access key for current account. (Backward compat wrapper)"""
    return _get_service().get_my_key()


def verify_key(user: str, key: bytes) -> bool:
    """Verify if a user has a valid access key. (Backward compat wrapper)"""
    return _get_service().verify_key(user, key)


def log_access(patient_id: str) -> str:
    """Log patient access on blockchain. (Backward compat wrapper)"""
    return _get_service().log_access(patient_id)


def register_doctor(wallet: str) -> None:
    """Register a doctor wallet. (Backward compat wrapper)"""
    return _get_service().register_doctor(wallet)


def is_doctor(address: str) -> bool:
    """Check if an address is a registered doctor. (Backward compat wrapper)"""
    return _get_service().is_doctor(address)


def register_patient(patient_id: str, wallet: str) -> None:
    """Register a patient with their wallet. (Backward compat wrapper)"""
    return _get_service().register_patient(patient_id, wallet)


def is_patient(patient_id: str) -> bool:
    """Check if a patient ID is registered. (Backward compat wrapper)"""
    return _get_service().is_patient(patient_id)


def get_access_logs(patient_id: str) -> Tuple[list, list, list]:
    """Get access logs for a patient. (Backward compat wrapper)"""
    return _get_service().get_access_logs(patient_id)


def get_access_logs_as_patient(patient_id: str, private_key: str) -> Tuple[list, list, list]:
    """Get access logs as a patient using their private key. (Backward compat wrapper)"""
    return _get_service().get_access_logs_as_patient(patient_id, private_key)


def generate_emergency_access() -> str:
    """Generate an emergency access token. (Backward compat wrapper)"""
    return _get_service().generate_emergency_access()
