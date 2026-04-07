"""Patient Models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .health import HealthData, Alert


class PatientInfo(BaseModel):
    """Patient information"""
    patient_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    contact: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class PatientRecord(BaseModel):
    """Complete patient record"""
    patient_info: PatientInfo
    latest_vitals: Optional[HealthData] = None
    health_history: List[HealthData] = Field(default_factory=list)
    active_alerts: List[Alert] = Field(default_factory=list)
    access_logs: List[str] = Field(default_factory=list)
