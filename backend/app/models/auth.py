"""Authentication Models"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"
    ADMIN = "ADMIN"


class LoginRequest(BaseModel):
    """Login request"""
    address: str = Field(..., description="Wallet address or patient ID")
    key: str = Field(..., description="Access key or private key")


class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    role: Optional[UserRole] = None
    user_address: Optional[str] = None
    user_name: Optional[str] = None
    message: str = ""


class RefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str = Field(..., description="Valid refresh token")


class AccessKeyResponse(BaseModel):
    """Access key response"""
    success: bool
    key: Optional[str] = None
    message: Optional[str] = None
