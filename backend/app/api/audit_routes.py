"""Audit API Routes - Endpoints for viewing audit logs"""

from fastapi import APIRouter, Request, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime
from dataclasses import asdict

from app.middleware.rbac import require_role, require_authenticated, get_current_user
from app.services.audit_service import AuditService, AuditLog, AuditAction
from app.services.emergency_service import EmergencyService

router = APIRouter(prefix="/api/audit", tags=["audit"])
emergency_service = EmergencyService()


class AuditLogResponse:
    """Audit log response model"""
    timestamp: str
    actor_address: Optional[str]
    actor_role: Optional[str]
    action: str
    resource_id: Optional[str]
    resource_type: Optional[str]
    result: str
    details: dict
    ip_address: Optional[str]
    error_message: Optional[str]


@router.get("/my-logs", response_model=dict)
@require_authenticated()
async def get_my_logs(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Get current user's audit logs
    
    Returns activities performed by the authenticated user.
    Available to all authenticated users.
    """
    user = get_current_user(request)
    actor_address = user["address"]
    
    logs, total = AuditService.get_logs(
        actor_address=actor_address,
        limit=limit,
        offset=offset,
    )
    
    return {
        "data": [asdict(log) for log in logs],
        "pagination": {
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": (offset + limit) < total,
        },
    }


@router.get("/resource/{resource_id}")
@require_authenticated()
async def get_resource_access(
    request: Request,
    resource_id: str,
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get all access to a specific resource
    
    Doctors can view access logs for resources they accessed.
    Admins can view access to any resource.
    """
    user = get_current_user(request)
    
    logs = AuditService.get_resource_access(resource_id, limit=limit)
    
    # Filter based on role
    if user["role"] == "ADMIN":
        # Admins see all logs
        filtered_logs = logs
    else:
        # Non-admins can only see if they were the actor
        filtered_logs = [log for log in logs if log.actor_address == user["address"]]
    
    return {
        "resource_id": resource_id,
        "total_accesses": len(filtered_logs),
        "data": [asdict(log) for log in filtered_logs],
    }


@router.get("/patient-access/{patient_id}")
@require_authenticated()
async def get_patient_access_history(
    request: Request,
    patient_id: str,
    limit: int = Query(100, ge=1, le=500),
):
    """Get access history for a patient report (patient self or admin)."""
    user = get_current_user(request)

    if user["role"] not in {"PATIENT", "ADMIN"}:
        raise HTTPException(status_code=403, detail="Only patients or admins can view patient access history")

    if user["role"] == "PATIENT" and user["address"] != patient_id:
        raise HTTPException(status_code=403, detail="Cannot view access history for another patient")

    logs = AuditService.get_resource_access(patient_id, limit=limit)
    allowed_actions = {
        AuditAction.LOG_PATIENT_ACCESS.value,
        AuditAction.EMERGENCY_ACCESS.value,
        AuditAction.VIEW_PATIENT_DATA.value,
        AuditAction.VIEW_PATIENT_VITALS.value,
    }

    filtered_logs = [
        log for log in logs
        if log.action in allowed_actions and (log.actor_role or "").upper() == "DOCTOR"
    ]

    normalized_logs = []
    for log in filtered_logs:
        details = dict(log.details or {})
        if log.action == AuditAction.EMERGENCY_ACCESS.value:
            details["access_mode"] = "EMERGENCY"
        normalized_logs.append({**asdict(log), "details": details})

    # Merge emergency session lifecycle records so emergency usage is always visible
    emergency_events = []
    try:
        emergency_result = emergency_service.list_sessions(patient_id=patient_id, limit=500, offset=0)
        for session in emergency_result.get("data", []):
            doctor_address = session.get("doctor_address")
            status = (session.get("status") or "").upper()

            def _push_event(ts: Optional[str], stage: str):
                if not ts:
                    return
                emergency_events.append({
                    "timestamp": ts,
                    "actor_address": doctor_address,
                    "actor_role": "DOCTOR",
                    "action": AuditAction.EMERGENCY_ACCESS.value,
                    "resource_id": patient_id,
                    "resource_type": "PATIENT_DATA",
                    "result": "SUCCESS",
                    "details": {
                        "access_mode": "EMERGENCY",
                        "stage": stage,
                        "session_id": session.get("session_id") or session.get("id"),
                        "status": status,
                    },
                    "ip_address": None,
                    "error_message": None,
                })

            _push_event(session.get("requested_at"), "session_requested")
            _push_event(session.get("activated_at"), "session_activated")
            _push_event(session.get("closed_at"), "session_closed")
    except Exception:
        # Keep API resilient: if emergency merge fails, still return audit-based history.
        pass

    combined_logs = normalized_logs + emergency_events
    combined_logs.sort(key=lambda item: item.get("timestamp") or "", reverse=True)
    combined_logs = combined_logs[:limit]

    return {
        "patient_id": patient_id,
        "total_accesses": len(combined_logs),
        "data": combined_logs,
    }


@router.get("/activity/{user_address}")
@require_role("ADMIN")
async def get_user_activity(
    request: Request,
    user_address: str,
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get all activity for a specific user (ADMIN ONLY)
    
    Returns all actions performed by a user, including:
    - Login/logout events
    - Data access attempts
    - Emergency access usage
    - Administrative actions
    """
    logs = AuditService.get_user_activity(user_address, limit=limit)
    
    return {
        "user_address": user_address,
        "total_events": len(logs),
        "data": [asdict(log) for log in logs],
    }


@router.get("/logs")
@require_role("ADMIN")
async def get_all_logs(
    request: Request,
    action: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Get all audit logs with filtering (ADMIN ONLY)
    
    Query parameters:
    - action: Filter by action type (e.g., "EMERGENCY_ACCESS", "LOGIN_SUCCESS")
    - resource_id: Filter by resource ID
    - limit: Number of logs to return (1-500, default 100)
    - offset: Pagination offset (default 0)
    
    Returns paginated audit logs with full details.
    """
    logs, total = AuditService.get_logs(
        action=action,
        resource_id=resource_id,
        limit=limit,
        offset=offset,
    )
    
    return {
        "pagination": {
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": (offset + limit) < total,
        },
        "filters": {
            "action": action,
            "resource_id": resource_id,
        },
        "data": [asdict(log) for log in logs],
    }


@router.get("/failed-attempts")
@require_role("ADMIN")
async def get_failed_attempts(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get all failed/denied access attempts (ADMIN ONLY)
    
    Returns authentication failures, permission denials, and errors
    for security investigation.
    """
    logs = AuditService.get_failed_attempts(limit=limit)
    
    return {
        "total_failed": len(logs),
        "data": [asdict(log) for log in logs],
    }


@router.get("/critical-events")
@require_role("ADMIN")
async def get_critical_events(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
):
    """
    Get critical security events (ADMIN ONLY)
    
    Returns high-risk activities including:
    - Emergency access usage
    - Unauthorized access attempts
    - User deactivations
    - Role changes
    """
    logs = AuditService.get_critical_events(limit=limit)
    
    return {
        "total_critical": len(logs),
        "data": [asdict(log) for log in logs],
    }


@router.get("/stats")
@require_role("ADMIN")
async def get_audit_stats(request: Request):
    """
    Get audit log statistics (ADMIN ONLY)
    
    Returns:
    - Total logs stored
    - Unique users tracked
    - Action type distribution
    - Success/failure/denied distribution
    """
    stats = AuditService.get_stats()
    
    return {
        "stats": stats,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.delete("/clear-logs")
@require_role("ADMIN")
async def clear_logs(request: Request):
    """
    Clear all audit logs (ADMIN ONLY, TESTING ONLY)
    
    WARNING: This permanently deletes all audit logs in memory.
    Use only for testing. Production should not clear audit trails.
    """
    AuditService.clear_logs()
    
    return {
        "status": "success",
        "message": "All audit logs cleared (for testing only)",
    }
