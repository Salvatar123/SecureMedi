"""Doctor Models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


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
    """Request model for emergency access"""
    patient_id: str
    key: str
