"""Patient Management Routes"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timedelta
from app.models.patient import PatientRecord, PatientInfo
from app.models.health import HealthData, HealthStatus
from app.services.health_service import HealthService
from app.services.emergency_service import EmergencyService
from app.middleware.rbac import require_role, require_self_or_role, get_current_user
from app.services.audit_service import AuditService, AuditAction, AuditResult

router = APIRouter(prefix="/api/patients", tags=["patients"])
health_service = HealthService()
emergency_service = EmergencyService()


def _default_patient_trend(limit: int) -> List[HealthData]:
    """Build fallback patient trend data when no vitals are logged yet."""
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


@router.get("/{patient_id}", response_model=PatientRecord)
@require_self_or_role("DOCTOR", "ADMIN")
async def get_patient_record(patient_id: str, request: Request):
    """Get patient record with all data (users can access own, doctors/admins can access any)"""
    try:
        user = get_current_user(request)
        
        # Additional authorization check
        if user["role"] == "PATIENT" and user["address"] != patient_id:
            raise HTTPException(status_code=403, detail="Cannot access other patient's data")

        requested_access_type = (request.query_params.get("access_type") or "").strip().upper()
        if requested_access_type not in {"NORMAL", "EMERGENCY"}:
            requested_access_type = ""

        access_mode = "SELF"
        access_type_for_log = "SELF"
        if user["role"] == "DOCTOR":
            access_mode = emergency_service.get_access_mode(user["address"], patient_id)
            if not access_mode:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "message": "Emergency session required",
                        "code": "EMERGENCY_SESSION_REQUIRED",
                    },
                )
            access_type_for_log = requested_access_type or access_mode
        
        # TODO: Add actual patient lookup from registry
        patient_info = PatientInfo(patient_id=patient_id)
        
        vitals = health_service.get_latest_health_data(limit=1)
        latest = vitals[0] if vitals else None
        
        history = health_service.get_latest_health_data(limit=100)
        
        if user["role"] == "DOCTOR":
            AuditService.log_event(
                action=AuditAction.LOG_PATIENT_ACCESS,
                actor_address=user["address"],
                actor_role=user["role"],
                resource_id=patient_id,
                resource_type="PATIENT_DATA",
                result=AuditResult.SUCCESS,
                details={
                    "access_mode": access_mode,
                    "access_type": access_type_for_log,
                    "endpoint": "/api/patients/{patient_id}",
                },
            )

        return PatientRecord(
            patient_info=patient_info,
            latest_vitals=latest,
            health_history=history,
            active_alerts=[],
            access_logs=[]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}/vitals", response_model=List[HealthData])
@require_self_or_role("DOCTOR", "ADMIN")
async def get_patient_vitals(patient_id: str, limit: int = 100, request: Request = None):
    """Get patient vital signs history (users can access own, doctors/admins can access any)"""
    try:
        user = get_current_user(request)
        
        # Additional authorization check
        if user["role"] == "PATIENT" and user["address"] != patient_id:
            raise HTTPException(status_code=403, detail="Cannot access other patient's vitals")

        requested_access_type = (request.query_params.get("access_type") or "").strip().upper()
        if requested_access_type not in {"NORMAL", "EMERGENCY"}:
            requested_access_type = ""

        access_mode = "SELF"
        access_type_for_log = "SELF"
        if user["role"] == "DOCTOR":
            access_mode = emergency_service.get_access_mode(user["address"], patient_id)
            if not access_mode:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "message": "Emergency session required",
                        "code": "EMERGENCY_SESSION_REQUIRED",
                    },
                )
            access_type_for_log = requested_access_type or access_mode
        
        if limit < 1:
            limit = 1
        if limit > 500:
            limit = 500

        data = health_service.get_latest_health_data(limit)
        if user["role"] == "DOCTOR":
            AuditService.log_event(
                action=AuditAction.LOG_PATIENT_ACCESS,
                actor_address=user["address"],
                actor_role=user["role"],
                resource_id=patient_id,
                resource_type="PATIENT_DATA",
                result=AuditResult.SUCCESS,
                details={
                    "access_mode": access_mode,
                    "access_type": access_type_for_log,
                    "endpoint": "/api/patients/{patient_id}/vitals",
                    "limit": limit,
                },
            )
        if data:
            return data

        return _default_patient_trend(limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PatientInfo])
@require_role("ADMIN", "DOCTOR")
async def list_patients(request: Request):
    """List all patients (admin and doctors only)"""
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
