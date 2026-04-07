"""Health Data Models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enum"""
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class HealthData(BaseModel):
    """Single health measurement"""
    heart_rate: int = Field(..., ge=0, le=250)
    temperature: float = Field(..., ge=20.0, le=50.0)
    spo2: int = Field(..., ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.now)
    status: HealthStatus = HealthStatus.NORMAL
    
    class Config:
        use_enum_values = True


class Alert(BaseModel):
    """Health alert"""
    id: str
    patient_id: str
    alert_type: str  # "CRITICAL", "WARNING", "INFO"
    message: str
    severity: int = Field(ge=1, le=5)
    timestamp: datetime = Field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
