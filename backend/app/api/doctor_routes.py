"""Doctor Operations Routes"""

import json
import os
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime
from app.models.doctor import (
    DoctorInfo,
    AccessLog,
    EmergencyAccessRequest,
    EmergencyActivateRequest,
    EmergencyCloseRequest,
)
try:
    from services.blockchain_service import BlockchainService
except ModuleNotFoundError:
    BlockchainService = None
from app.middleware.rbac import require_role, get_current_user
from app.services.audit_service import AuditService, AuditAction, AuditResult
from app.services.emergency_service import EmergencyService
from app.services.supabase_service import SupabaseService
from config.settings import get_settings

router = APIRouter(prefix="/api/doctors", tags=["doctors"])
ASSIGNMENTS_FILE = "doctor_patient_assignments.json"

# Initialize blockchain service with error handling
try:
    blockchain_service = BlockchainService() if BlockchainService else None
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to initialize BlockchainService: {e}")
    blockchain_service = None

settings = get_settings()
supabase_service = None
if settings.ENABLE_SUPABASE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        supabase_service = SupabaseService(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to initialize SupabaseService: {e}")

    emergency_service = EmergencyService()


def _load_assignments() -> dict:
    if not os.path.exists(ASSIGNMENTS_FILE):
        return {}
    try:
        with open(ASSIGNMENTS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


@router.get("/{doctor_address}", response_model=DoctorInfo)
@require_role("DOCTOR", "PATIENT", "ADMIN")
async def get_doctor_info(doctor_address: str, request: Request):
    """Get doctor information (authenticated users only)"""
    try:
        # TODO: Load from blockchain registry
        return DoctorInfo(address=doctor_address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doctor_address}/access-logs", response_model=List[AccessLog])
@require_role("DOCTOR", "ADMIN")
async def get_access_logs(doctor_address: str, limit: int = 100, request: Request = None):
    """Get doctor's patient access logs (doctors and admins only)"""
    try:
        user = get_current_user(request)
        
        # Doctors can only see their own logs
        if user["role"] == "DOCTOR" and user["address"] != doctor_address:
            raise HTTPException(status_code=403, detail="Can only view your own access logs")
        
        # TODO: Load from blockchain
        return []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doctor_address}/assigned-patients")
@require_role("DOCTOR", "ADMIN")
async def get_assigned_patients(doctor_address: str, request: Request = None):
    """Get patients assigned to a doctor (doctor self or admin)."""
    try:
        user = get_current_user(request)
        if user["role"] == "DOCTOR" and user["address"].lower() != doctor_address.lower():
            raise HTTPException(status_code=403, detail="Can only view your own assigned patients")

        if not supabase_service:
            return {
                "success": False,
                "message": "Supabase service is not available",
                "data": [],
                "total": 0,
            }

        doctor_result = (
            supabase_service.client
            .table("doctors")
            .select("id,name,wallet_address")
            .eq("wallet_address", doctor_address.lower())
            .limit(1)
            .execute()
        )

        if not doctor_result.data:
            return {
                "success": True,
                "message": "Doctor not found in registry",
                "data": [],
                "total": 0,
            }

        doctor = doctor_result.data[0]
        doctor_id = str(doctor.get("id"))

        assignments = _load_assignments()
        assigned_patient_ids = [
            patient_id
            for patient_id, assignment in assignments.items()
            if assignment.get("doctor_id") == doctor_id
        ]

        if not assigned_patient_ids:
            return {
                "success": True,
                "data": [],
                "total": 0,
                "doctor": {
                    "id": doctor_id,
                    "name": doctor.get("name"),
                    "wallet_address": doctor.get("wallet_address"),
                },
            }

        patients_result = (
            supabase_service.client
            .table("patients")
            .select("id,patient_id,name,email,status,wallet_address")
            .in_("id", assigned_patient_ids)
            .execute()
        )

        patients = patients_result.data or []
        for patient in patients:
            assignment = assignments.get(str(patient.get("id")), {})
            patient["assigned_at"] = assignment.get("assigned_at")

        return {
            "success": True,
            "data": patients,
            "total": len(patients),
            "doctor": {
                "id": doctor_id,
                "name": doctor.get("name"),
                "wallet_address": doctor.get("wallet_address"),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doctor_address}/access-patient/{patient_id}")
@require_role("DOCTOR")
async def log_patient_access(doctor_address: str, patient_id: str, request: Request = None):
    """Log doctor's access to patient record (doctors only)"""
    try:
        user = get_current_user(request)

        body = {}
        try:
            body = await request.json()
            if not isinstance(body, dict):
                body = {}
        except Exception:
            body = {}

        # Accept both JSON body and query params for compatibility.
        access_type = (
            body.get("access_type")
            or request.query_params.get("access_type")
            or "NORMAL"
        )
        reason = (
            body.get("reason")
            or request.query_params.get("reason")
            or ""
        )
        access_type = str(access_type).upper()
        
        # Doctors can only log access for themselves
        if user["address"] != doctor_address:
            AuditService.log_event(
                action=AuditAction.UNAUTHORIZED_ACCESS_ATTEMPT,
                actor_address=user["address"],
                actor_role=user["role"],
                resource_id=patient_id,
                resource_type="PATIENT_DATA",
                result=AuditResult.DENIED,
                error_message="Attempted to log access for another doctor",
            )
            raise HTTPException(status_code=403, detail="Can only log access for yourself")
        
        # TODO: Write to blockchain
        AuditService.log_event(
            action=AuditAction.LOG_PATIENT_ACCESS,
            actor_address=user["address"],
            actor_role=user["role"],
            resource_id=patient_id,
            resource_type="PATIENT_DATA",
            result=AuditResult.SUCCESS,
            details={"access_type": access_type, "reason": reason},
        )
        
        return {
            "success": True,
            "message": "Access logged",
            "access_type": access_type,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        user = get_current_user(request)
        AuditService.log_event(
            action=AuditAction.LOG_PATIENT_ACCESS,
            actor_address=user["address"],
            actor_role=user["role"],
            resource_id=patient_id,
            resource_type="PATIENT_DATA",
            result=AuditResult.FAILURE,
            error_message=str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{doctor_address}/generate-key")
@require_role("DOCTOR")
async def generate_access_key(doctor_address: str, request: Request = None):
    """Generate new access key for doctor (doctors only)"""
    try:
        user = get_current_user(request)
        
        # Doctors can only generate keys for themselves
        if user["address"] != doctor_address:
            raise HTTPException(status_code=403, detail="Can only generate keys for yourself")
        
        # TODO: Generate and store in blockchain
        return {
            "success": True,
            "key": "0x" + "abcd1234" * 8,
            "message": "Access key generated"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emergency/request")
@require_role("DOCTOR")
async def request_emergency_access(request_data: EmergencyAccessRequest, request: Request):
    """Create a break-glass emergency session for a patient."""
    user = get_current_user(request)
    try:
        if emergency_service.is_doctor_assigned(user["address"], request_data.patient_id):
            raise HTTPException(status_code=400, detail="Patient is already assigned; normal access should be used")

        session = emergency_service.create_session(
            doctor_address=user["address"],
            patient_id=request_data.patient_id,
            reason=request_data.reason,
            severity=request_data.severity,
            expected_duration_min=request_data.expected_duration_min,
            ip_address=request.client.host if request.client else None,
        )

        AuditService.log_event(
            action=AuditAction.EMERGENCY_ACCESS,
            actor_address=user["address"],
            actor_role=user["role"],
            resource_id=request_data.patient_id,
            resource_type="PATIENT_DATA",
            result=AuditResult.SUCCESS,
            details={
                "stage": "request_created",
                "session_id": session["session_id"],
                "severity": session["severity"],
                "expected_duration_min": session["expected_duration_min"],
                "reason": session["reason"],
            },
        )

        return {
            "success": True,
            "session_id": session["session_id"],
            "status": session["status"],
            "requested_at": session["requested_at"],
            "message": "Emergency request created",
        }
    except HTTPException:
        raise
    except Exception as e:
        AuditService.log_event(
            action=AuditAction.EMERGENCY_ACCESS,
            actor_address=user["address"],
            actor_role=user["role"],
            resource_id=request_data.patient_id,
            resource_type="PATIENT_DATA",
            result=AuditResult.FAILURE,
            details={"stage": "request_create_failed"},
            error_message=str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emergency/{session_id}/activate")
@require_role("DOCTOR")
async def activate_emergency_access(session_id: str, payload: EmergencyActivateRequest, request: Request):
    """Activate a pending emergency session and grant temporary access."""
    user = get_current_user(request)
    try:
        blockchain_tx_hash = None
        if blockchain_service is not None:
            try:
                blockchain_tx_hash = blockchain_service.generate_emergency_access()
            except Exception:
                # Emergency workflow should still proceed even if chain anchoring fails.
                blockchain_tx_hash = None

        session = emergency_service.activate_session(
            session_id=session_id,
            doctor_address=user["address"],
            activation_note=payload.activation_note,
            blockchain_tx_hash=blockchain_tx_hash,
        )

        AuditService.log_event(
            action=AuditAction.EMERGENCY_ACCESS,
            actor_address=user["address"],
            actor_role=user["role"],
            resource_id=session["patient_id"],
            resource_type="PATIENT_DATA",
            result=AuditResult.SUCCESS,
            details={
                "stage": "session_activated",
                "session_id": session_id,
                "expires_at": session.get("expires_at"),
                "blockchain_tx_hash": blockchain_tx_hash,
            },
        )

        return {
            "success": True,
            "session_id": session["session_id"],
            "status": session["status"],
            "activated_at": session["activated_at"],
            "expires_at": session["expires_at"],
            "blockchain_tx_hash": session.get("blockchain_tx_hash"),
            "message": "Emergency session activated",
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency/{session_id}/close")
@require_role("DOCTOR", "ADMIN")
async def close_emergency_access(session_id: str, payload: EmergencyCloseRequest, request: Request):
    """Close an emergency session and record final outcome."""
    user = get_current_user(request)
    try:
        session = emergency_service.close_session(
            session_id=session_id,
            actor_address=user["address"],
            actor_role=user["role"],
            closure_note=payload.closure_note,
            outcome=payload.outcome,
        )

        AuditService.log_event(
            action=AuditAction.EMERGENCY_ACCESS,
            actor_address=user["address"],
            actor_role=user["role"],
            resource_id=session["patient_id"],
            resource_type="PATIENT_DATA",
            result=AuditResult.SUCCESS,
            details={
                "stage": "session_closed",
                "session_id": session_id,
                "outcome": session.get("outcome"),
            },
        )

        return {
            "success": True,
            "session_id": session["session_id"],
            "status": session["status"],
            "closed_at": session.get("closed_at"),
            "message": "Emergency session closed",
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emergency/{session_id}/status")
@require_role("DOCTOR", "ADMIN")
async def get_emergency_status(session_id: str, request: Request):
    """Get current emergency session status and time remaining."""
    user = get_current_user(request)
    try:
        session = emergency_service.get_status(session_id)

        if user["role"] == "DOCTOR" and session.get("doctor_address", "").lower() != user["address"].lower():
            raise HTTPException(status_code=403, detail="Can only view your own emergency sessions")

        return {"success": True, **session}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
