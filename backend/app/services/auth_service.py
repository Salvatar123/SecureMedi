"""Authentication Service - Wraps blockchain for auth"""

import sys
import os
import logging
from typing import Optional, Tuple

# Add parent paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from blockchain.connector import BlockchainConnector
from app.models.auth import AuthResponse, UserRole

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        """Initialize blockchain connector"""
        try:
            self.blockchain = BlockchainConnector()
        except Exception as e:
            logger.warning(f"Blockchain unavailable: {e}")
            self.blockchain = None
    
    def verify_doctor(self, address: str, key: bytes) -> Tuple[bool, str]:
        """Verify doctor credentials"""
        try:
            if not self.blockchain:
                return False, "Blockchain service unavailable"
            
            if not self.blockchain.is_doctor(address):
                return False, "Not a registered doctor"
            
            # Verify key signature
            valid = self.blockchain.verify_key(address, key)
            if valid:
                return True, "Doctor verified"
            else:
                return False, "Invalid key"
        except Exception as e:
            logger.error(f"Doctor verification error: {e}")
            return False, str(e)
    
    def verify_patient(self, patient_id: str, private_key: str) -> Tuple[bool, str]:
        """Verify patient credentials"""
        try:
            # In a real system, verify against stored patient records
            # For now, basic validation
            if not patient_id or not private_key:
                return False, "Invalid credentials"
            
            return True, "Patient verified"
        except Exception as e:
            logger.error(f"Patient verification error: {e}")
            return False, str(e)
    
    def generate_access_token(self, address: str, role: UserRole) -> str:
        """Generate JWT token"""
        # This would use PyJWT to create proper tokens
        # For now, return simple token
        return f"token_{role}_{address[:10]}"
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[str], Optional[UserRole]]:
        """Verify and decode JWT token"""
        try:
            if not token:
                return False, None, None
            
            # Parse token format: token_ROLE_ADDRESS
            parts = token.split("_")
            if len(parts) != 3 or parts[0] != "token":
                return False, None, None
            
            role = UserRole(parts[1])
            address = parts[2]
            
            return True, address, role
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return False, None, None
