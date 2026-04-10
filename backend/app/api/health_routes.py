"""Health Monitoring Routes"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timedelta
from app.models.health import HealthData, Alert, HealthStatus
from app.services.health_service import HealthService
from app.services.emergency_service import EmergencyService
from app.middleware.rbac import require_role, get_current_user

router = APIRouter(prefix="/api/health", tags=["health"])
health_service = HealthService()
emergency_service = EmergencyService()


def _default_trend_data(limit: int) -> List[HealthData]:
    """Build fallback trend data for dashboard charts when no logs are available."""
    points = max(6, min(limit, 24))
    now = datetime.now()

    heart_pattern = [72, 74, 73, 75, 71, 72, 74, 73]
    temp_pattern = [36.6, 36.7, 36.6, 36.8, 36.7, 36.6, 36.7, 36.6]
    spo2_pattern = [98, 98, 97, 98, 99, 98, 97, 98]

    trend: List[HealthData] = []
    for i in range(points):
        idx = i % len(heart_pattern)
        trend.append(
            HealthData(
                heart_rate=heart_pattern[idx],
                temperature=temp_pattern[idx],
                spo2=spo2_pattern[idx],
                timestamp=now - timedelta(minutes=(points - i) * 5),
                status=HealthStatus.NORMAL,
            )
        )

    return trend


@router.get("/vitals/latest", response_model=HealthData)
@require_role("DOCTOR", "PATIENT")
async def get_latest_vitals(request: Request):
    """Get latest vital signs (Doctors and Patients only)"""
    try:
        data = health_service.get_latest_health_data(limit=1)
        if data:
            return data[0]
        return HealthData(
            heart_rate=72,
            temperature=36.6,
            spo2=98,
            status=HealthStatus.NORMAL,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vitals/history", response_model=List[HealthData])
@require_role("DOCTOR", "PATIENT")
async def get_vitals_history(limit: int = 100, request: Request = None):
    """Get vitals history (Doctors and Patients only)"""
    try:
        if limit < 1:
            limit = 1
        if limit > 500:
            limit = 500

        data = health_service.get_latest_health_data(limit)
        if data:
            return data

        return _default_trend_data(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
@require_role("DOCTOR", "PATIENT")
async def get_health_statistics(request: Request):
    """Get health statistics (Doctors and Patients only)"""
    try:
        return health_service.get_health_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[Alert])
@require_role("DOCTOR", "PATIENT")
async def get_active_alerts(patient_id: str = None, request: Request = None):
    """Get active health alerts (Doctors and Patients only)"""
    try:
        user = get_current_user(request)
        
        # Patients can only see their own alerts
        if user["role"] == "PATIENT" and patient_id and patient_id != user["address"]:
            raise HTTPException(
                status_code=403,
                detail="Patients can only view their own alerts"
            )

        if user["role"] == "DOCTOR" and patient_id and not emergency_service.has_active_access(user["address"], patient_id):
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Emergency session required",
                    "code": "EMERGENCY_SESSION_REQUIRED",
                },
            )
        
        return health_service.get_alerts(patient_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vitals")
async def log_vitals(data: HealthData):
    """Log new vital signs"""
    try:
        success = health_service.log_health_data(data)
        return {"success": success, "message": "Vitals logged" if success else "Failed to log vitals"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
