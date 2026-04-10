"""Doctor Models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DoctorInfo(BaseModel):
    """Doctor information"""
    address: str
    name: Optional[str] = None
    specialization: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class AccessLog(BaseModel):
    """Patient access log"""
    doctor_address: str
    patient_id: str
    access_type: str  # "NORMAL", "EMERGENCY"
    timestamp: datetime = Field(default_factory=datetime.now)
    reason: Optional[str] = None


class EmergencyAccessRequest(BaseModel):
    """Request model for creating an emergency access session"""
    patient_id: str
    reason: str
    severity: str = "CRITICAL"
    expected_duration_min: int = 30


class EmergencyActivateRequest(BaseModel):
    """Request model for activating a pending emergency session"""
    activation_note: Optional[str] = None


class EmergencyCloseRequest(BaseModel):
    """Request model for closing an active emergency session"""
    closure_note: str
    outcome: str = "UNKNOWN"
