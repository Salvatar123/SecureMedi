"""JWT Token Service - Handles JWT generation, validation, and refresh"""

import jwt
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class JWTService:
    """Service for JWT token operations with RS256 signing"""
    
    # Token expiration times
    ACCESS_TOKEN_EXPIRY = 15  # minutes
    REFRESH_TOKEN_EXPIRY = 7  # days
    
    # In-memory token blacklist (maps jti -> expiration_time)
    # In production, use Redis
    _token_blacklist: Dict[str, datetime] = {}
    
    def __init__(self):
        """Initialize JWT service with RSA keys"""
        self.private_key = self._load_or_generate_private_key()
        self.public_key = self._load_or_generate_public_key()
        self.algorithm = "RS256"
    
    @staticmethod
    def _load_or_generate_private_key() -> str:
        """Load private key from environment or generate new one"""
        # Check environment variable first (for production)
        private_key = os.getenv("JWT_PRIVATE_KEY")
        if private_key:
            return private_key
        
        # For development, check if key file exists
        key_path = "config/jwt_private_key.pem"
        if os.path.exists(key_path):
            with open(key_path, "r") as f:
                return f.read()
        
        # Generate new key for development
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        
        logger.warning("Generating new RSA private key for development. Set JWT_PRIVATE_KEY in production.")
        
        private_key_obj = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        private_key_pem = private_key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("utf-8")
        
        # Save for development
        os.makedirs("config", exist_ok=True)
        with open(key_path, "w") as f:
            f.write(private_key_pem)
        
        return private_key_pem
    
    @staticmethod
    def _load_or_generate_public_key() -> str:
        """Load or generate public key from private key"""
        public_key = os.getenv("JWT_PUBLIC_KEY")
        if public_key:
            return public_key
        
        key_path = "config/jwt_public_key.pem"
        if os.path.exists(key_path):
            with open(key_path, "r") as f:
                return f.read()
        
        # Generate from private key
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        
        private_key_pem = JWTService._load_or_generate_private_key()
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        
        private_key_obj = load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        public_key_obj = private_key_obj.public_key()
        public_key_pem = public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8")
        
        # Save for development
        os.makedirs("config", exist_ok=True)
        with open(key_path, "w") as f:
            f.write(public_key_pem)
        
        return public_key_pem
    
    def generate_access_token(self, user_address: str, role: str) -> str:
        """
        Generate access token (15 minutes expiry)
        
        Args:
            user_address: User's wallet address or patient ID
            role: User role (DOCTOR, PATIENT, ADMIN)
        
        Returns:
            JWT access token
        """
        jti = str(uuid4())  # Unique token ID for revocation
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(minutes=self.ACCESS_TOKEN_EXPIRY)
        
        payload = {
            "sub": user_address,  # Subject (user identifier)
            "role": role,
            "type": "access",
            "jti": jti,  # JWT ID for revocation
            "iat": now,  # Issued at
            "exp": expiry,  # Expiration
        }
        
        token = jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        logger.info(f"Generated access token for {user_address} ({role})")
        return token
    
    def generate_refresh_token(self, user_address: str, role: str) -> str:
        """
        Generate refresh token (7 days expiry)
        
        Args:
            user_address: User's wallet address or patient ID
            role: User role (DOCTOR, PATIENT, ADMIN)
        
        Returns:
            JWT refresh token
        """
        jti = str(uuid4())
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(days=self.REFRESH_TOKEN_EXPIRY)
        
        payload = {
            "sub": user_address,
            "role": role,
            "type": "refresh",
            "jti": jti,
            "iat": now,
            "exp": expiry,
        }
        
        token = jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        logger.info(f"Generated refresh token for {user_address} ({role})")
        return token
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Tuple of (is_valid, decoded_payload, error_message)
        """
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            
            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti in self._token_blacklist:
                blacklist_expiry = self._token_blacklist[jti]
                if datetime.now(timezone.utc) < blacklist_expiry:
                    return False, None, "Token has been revoked"
            
            return True, payload, None
        
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {str(e)}"
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return False, None, "Token verification failed"
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            Tuple of (success, new_access_token, error_message)
        """
        is_valid, payload, error = self.verify_token(refresh_token)
        
        if not is_valid:
            return False, None, error
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return False, None, "Token is not a refresh token"
        
        # Generate new access token with same claims
        user_address = payload.get("sub")
        role = payload.get("role")
        
        if not user_address or not role:
            return False, None, "Invalid refresh token claims"
        
        new_access_token = self.generate_access_token(user_address, role)
        return True, new_access_token, None
    
    def revoke_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Add token to blacklist (for logout)
        
        Args:
            token: JWT token to revoke
        
        Returns:
            Tuple of (success, error_message)
        """
        is_valid, payload, error = self.verify_token(token)
        
        if not is_valid:
            return False, error
        
        jti = payload.get("jti")
        expiry = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        
        # Add token to blacklist
        self._token_blacklist[jti] = expiry
        logger.info(f"Revoked token: {jti}")
        
        # Clean up expired tokens from blacklist (every 50 revocations)
        if len(self._token_blacklist) % 50 == 0:
            self._cleanup_blacklist()
        
        return True, None
    
    @classmethod
    def _cleanup_blacklist(cls):
        """Remove expired tokens from blacklist"""
        now = datetime.now(timezone.utc)
        expired_jtis = [jti for jti, expiry in cls._token_blacklist.items() if expiry < now]
        
        for jti in expired_jtis:
            del cls._token_blacklist[jti]
        
        if expired_jtis:
            logger.debug(f"Cleaned up {len(expired_jtis)} expired tokens from blacklist")
    
    def get_token_info(self, token: str) -> Optional[Dict]:
        """Get token information without full validation (use with caution)"""
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            # Return expired token info for debugging
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm], options={"verify_exp": False})
            return payload
        except Exception:
            return None
