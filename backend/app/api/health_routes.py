"""Health Monitoring Routes"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.health import HealthData, Alert
from app.services.health_service import HealthService

router = APIRouter(prefix="/api/health", tags=["health"])
health_service = HealthService()


@router.get("/vitals/latest", response_model=HealthData)
async def get_latest_vitals():
    """Get latest vital signs"""
    try:
        data = health_service.get_latest_health_data(limit=1)
        if data:
            return data[0]
        return HealthData(heart_rate=0, temperature=0, spo2=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vitals/history", response_model=List[HealthData])
async def get_vitals_history(limit: int = 100):
    """Get vitals history"""
    try:
        if limit > 500:
            limit = 500
        return health_service.get_latest_health_data(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_health_statistics():
    """Get health statistics"""
    try:
        return health_service.get_health_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[Alert])
async def get_active_alerts(patient_id: str = None):
    """Get active health alerts"""
    try:
        return health_service.get_alerts(patient_id)
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
