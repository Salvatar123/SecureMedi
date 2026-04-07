"""Patient Management Routes"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.patient import PatientRecord, PatientInfo
from app.models.health import HealthData
from app.services.health_service import HealthService

router = APIRouter(prefix="/api/patients", tags=["patients"])
health_service = HealthService()


@router.get("/{patient_id}", response_model=PatientRecord)
async def get_patient_record(patient_id: str):
    """Get patient record with all data"""
    try:
        # TODO: Add actual patient lookup from registry
        patient_info = PatientInfo(patient_id=patient_id)
        
        vitals = health_service.get_latest_health_data(limit=1)
        latest = vitals[0] if vitals else None
        
        history = health_service.get_latest_health_data(limit=100)
        
        return PatientRecord(
            patient_info=patient_info,
            latest_vitals=latest,
            health_history=history,
            active_alerts=[],
            access_logs=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}/vitals", response_model=List[HealthData])
async def get_patient_vitals(patient_id: str, limit: int = 100):
    """Get patient vital signs history"""
    try:
        return health_service.get_latest_health_data(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PatientInfo])
async def list_patients():
    """List all patients (admin only)"""
    try:
        # TODO: Load from registry
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{patient_id}/export")
async def export_patient_data(patient_id: str):
    """Export patient data as CSV"""
    try:
        record = await get_patient_record(patient_id)
        
        import csv
        import io
        from datetime import datetime
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Timestamp", "Heart Rate", "Temperature", "SpO2", "Status"])
        
        # Write vitals
        for vital in record.health_history:
            writer.writerow([
                vital.timestamp.isoformat(),
                vital.heart_rate,
                vital.temperature,
                vital.spo2,
                vital.status
            ])
        
        return {
            "filename": f"patient_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "data": output.getvalue()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
