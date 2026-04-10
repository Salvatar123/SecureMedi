"""Authentication Service - Wraps blockchain for auth"""

import sys
import os
import logging
from typing import Optional, Tuple, Dict

# Add parent paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

try:
    from blockchain.connector import BlockchainConnector
except ModuleNotFoundError:
    BlockchainConnector = None
from app.models.auth import AuthResponse, UserRole
from app.services.jwt_service import JWTService
from app.services.audit_service import AuditService, AuditAction, AuditResult
from app.services.wallet_service import get_wallet_service
import secrets
from eth_account import Account
from config.settings import get_settings
from app.services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        """Initialize blockchain connector and JWT service"""
        if BlockchainConnector is None:
            logger.warning("Blockchain connector module not available; continuing without blockchain auth checks")
            self.blockchain = None
        else:
            try:
                self.blockchain = BlockchainConnector()
            except Exception as e:
                logger.warning(f"Blockchain unavailable: {e}")
                self.blockchain = None

        settings = get_settings()
        self.supabase = None
        if settings.ENABLE_SUPABASE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.supabase = SupabaseService(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            except Exception as e:
                logger.warning(f"Supabase unavailable in auth service: {e}")
        
        # Initialize JWT service
        self.jwt_service = JWTService()
    
    def verify_doctor(self, address: str, private_key: str) -> Tuple[bool, str]:
        """Verify doctor credentials using wallet address + private key"""
        try:
            normalized_key = (private_key or "").strip().replace("0x", "")
            if not normalized_key:
                AuditService.log_event(
                    action=AuditAction.LOGIN_FAILED,
                    actor_address=address,
                    actor_role="DOCTOR",
                    result=AuditResult.FAILURE,
                    error_message="Missing private key",
                )
                return False, "Private key is required"

            try:
                derived_address = Account.from_key(bytes.fromhex(normalized_key)).address
            except Exception:
                AuditService.log_event(
                    action=AuditAction.LOGIN_FAILED,
                    actor_address=address,
                    actor_role="DOCTOR",
                    result=AuditResult.FAILURE,
                    error_message="Invalid private key format",
                )
                return False, "Invalid private key format"

            if derived_address.lower() != address.lower():
                AuditService.log_event(
                    action=AuditAction.LOGIN_FAILED,
                    actor_address=address,
                    actor_role="DOCTOR",
                    result=AuditResult.FAILURE,
                    error_message="Private key does not match wallet address",
                )
                return False, "Private key does not match wallet address"

            registered_on_chain = False
            if self.blockchain:
                try:
                    registered_on_chain = self.blockchain.is_doctor(address)
                except Exception as e:
                    logger.warning(f"Blockchain doctor check failed for {address}: {e}")

            registered_in_db = False
            if self.supabase:
                try:
                    doctor = self.supabase.get_doctor_by_address(address)
                    registered_in_db = bool(doctor) and doctor.get("status", "active") != "inactive"
                except Exception as e:
                    logger.warning(f"Supabase doctor check failed for {address}: {e}")

            if not registered_on_chain and not registered_in_db:
                AuditService.log_event(
                    action=AuditAction.LOGIN_FAILED,
                    actor_address=address,
                    actor_role="DOCTOR",
                    result=AuditResult.FAILURE,
                    error_message="Not a registered doctor",
                )
                return False, "Not a registered doctor"

            AuditService.log_event(
                action=AuditAction.LOGIN_SUCCESS,
                actor_address=address,
                actor_role="DOCTOR",
                resource_id=address,
                resource_type="SESSION",
                result=AuditResult.SUCCESS,
                details={"login_type": "doctor_private_key"},
            )
            return True, "Doctor verified"
        except Exception as e:
            logger.error(f"Doctor verification error: {e}")
            AuditService.log_event(
                action=AuditAction.LOGIN_FAILED,
                actor_address=address,
                actor_role="DOCTOR",
                result=AuditResult.FAILURE,
                error_message=str(e),
            )
            return False, str(e)
    
    def verify_patient(self, patient_id: str, private_key: str) -> Tuple[bool, str]:
        """Verify patient credentials"""
        try:
            if not patient_id or not private_key:
                AuditService.log_event(
                    action=AuditAction.LOGIN_FAILED,
                    actor_address=patient_id,
                    actor_role="PATIENT",
                    result=AuditResult.FAILURE,
                    error_message="Invalid credentials",
                )
                return False, "Invalid credentials"

            normalized_key = (private_key or "").strip().replace("0x", "")
            if not normalized_key:
                AuditService.log_event(
                    action=AuditAction.LOGIN_FAILED,
                    actor_address=patient_id,
                    actor_role="PATIENT",
                    result=AuditResult.FAILURE,
                    error_message="Missing private key",
                )
                return False, "Private key is required"

            try:
                derived_address = Account.from_key(bytes.fromhex(normalized_key)).address.lower()
            except Exception:
                AuditService.log_event(
                    action=AuditAction.LOGIN_FAILED,
                    actor_address=patient_id,
                    actor_role="PATIENT",
                    result=AuditResult.FAILURE,
                    error_message="Invalid private key format",
                )
                return False, "Invalid private key format"

            patient_record = None
            if self.supabase:
                try:
                    patient_record = self.supabase.get_patient_by_id(patient_id)
                except Exception as e:
                    logger.warning(f"Supabase patient lookup failed for {patient_id}: {e}")

            if patient_record:
                if patient_record.get("status", "active") == "inactive":
                    AuditService.log_event(
                        action=AuditAction.LOGIN_FAILED,
                        actor_address=patient_id,
                        actor_role="PATIENT",
                        result=AuditResult.FAILURE,
                        error_message="Patient account inactive",
                    )
                    return False, "Patient account is inactive"

                wallet_address = (patient_record.get("wallet_address") or "").lower()
                if wallet_address and wallet_address != derived_address:
                    AuditService.log_event(
                        action=AuditAction.LOGIN_FAILED,
                        actor_address=patient_id,
                        actor_role="PATIENT",
                        result=AuditResult.FAILURE,
                        error_message="Private key does not match patient wallet",
                    )
                    return False, "Private key does not match patient wallet"
            else:
                # Fallback to local wallet assignment file for environments without Supabase.
                wallet_service = get_wallet_service()
                wallet_record = wallet_service.get_wallet(patient_id)

                if wallet_record:
                    expected_address = (wallet_record.get("address") or "").lower()
                    if expected_address and expected_address != derived_address:
                        AuditService.log_event(
                            action=AuditAction.LOGIN_FAILED,
                            actor_address=patient_id,
                            actor_role="PATIENT",
                            result=AuditResult.FAILURE,
                            error_message="Private key does not match patient wallet",
                        )
                        return False, "Private key does not match patient wallet"
                elif self.blockchain:
                    # Final fallback: on-chain patient existence only.
                    try:
                        if not self.blockchain.is_patient(patient_id):
                            AuditService.log_event(
                                action=AuditAction.LOGIN_FAILED,
                                actor_address=patient_id,
                                actor_role="PATIENT",
                                result=AuditResult.FAILURE,
                                error_message="Patient not registered",
                            )
                            return False, "Patient not registered"
                    except Exception as e:
                        logger.warning(f"Blockchain patient check failed for {patient_id}: {e}")
                else:
                    AuditService.log_event(
                        action=AuditAction.LOGIN_FAILED,
                        actor_address=patient_id,
                        actor_role="PATIENT",
                        result=AuditResult.FAILURE,
                        error_message="Patient not found",
                    )
                    return False, "Patient not found"
            
            AuditService.log_event(
                action=AuditAction.LOGIN_SUCCESS,
                actor_address=patient_id,
                actor_role="PATIENT",
                resource_id=patient_id,
                resource_type="SESSION",
                result=AuditResult.SUCCESS,
                details={"login_type": "patient"},
            )
            return True, "Patient verified"
        except Exception as e:
            logger.error(f"Patient verification error: {e}")
            AuditService.log_event(
                action=AuditAction.LOGIN_FAILED,
                actor_address=patient_id,
                actor_role="PATIENT",
                result=AuditResult.FAILURE,
                error_message=str(e),
            )
            return False, str(e)
    
    def generate_access_token(self, address: str, role: UserRole) -> str:
        """Generate JWT access token (15 min expiry)"""
        return self.jwt_service.generate_access_token(address, role.value)

    def get_doctor_name(self, address: str) -> Optional[str]:
        """Resolve doctor display name for authenticated sessions."""
        if not self.supabase:
            return None
        try:
            doctor = self.supabase.get_doctor_by_address(address)
            if doctor:
                return doctor.get("name")
        except Exception as e:
            logger.warning(f"Failed to fetch doctor name for {address}: {e}")
        return None

    def get_patient_name(self, patient_id: str) -> Optional[str]:
        """Resolve patient display name for authenticated sessions."""
        if not self.supabase:
            return None
        try:
            patient = self.supabase.get_patient_by_id(patient_id)
            if patient:
                return patient.get("name")
        except Exception as e:
            logger.warning(f"Failed to fetch patient name for {patient_id}: {e}")
        return None
    
    def generate_refresh_token(self, address: str, role: UserRole) -> str:
        """Generate JWT refresh token (7 day expiry)"""
        return self.jwt_service.generate_refresh_token(address, role.value)
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[str], Optional[UserRole]]:
        """Verify JWT token and extract user info"""
        is_valid, payload, error = self.jwt_service.verify_token(token)
        
        if not is_valid:
            logger.warning(f"Token verification failed: {error}")
            return False, None, None
        
        try:
            address = payload.get("sub")
            role_str = payload.get("role")
            
            if not address or not role_str:
                return False, None, None
            
            role = UserRole(role_str)
            return True, address, role
        except Exception as e:
            logger.error(f"Token payload parsing error: {e}")
            return False, None, None
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate new access token from refresh token"""
        return self.jwt_service.refresh_access_token(refresh_token)
    
    def logout(self, token: str) -> Tuple[bool, Optional[str]]:
        """Revoke token on logout"""
        # Extract user info from token if possible
        is_valid, payload, error = self.jwt_service.verify_token(token)
        
        if is_valid:
            user_address = payload.get("sub")
            user_role = payload.get("role")
            
            AuditService.log_event(
                action=AuditAction.LOGOUT,
                actor_address=user_address,
                actor_role=user_role,
                resource_id=user_address,
                resource_type="SESSION",
                result=AuditResult.SUCCESS,
            )
        
        return self.jwt_service.revoke_token(token)
    
    def generate_random_key(self) -> str:
        """Generates a secure random access key for emergency access"""
        return os.urandom(32).hex()
