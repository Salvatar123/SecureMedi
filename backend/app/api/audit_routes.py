"""Audit API Routes - Endpoints for viewing audit logs"""

from fastapi import APIRouter, Request, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime
from dataclasses import asdict

from app.middleware.rbac import require_role, require_authenticated, get_current_user
from app.services.audit_service import AuditService, AuditLog

router = APIRouter(prefix="/api/audit", tags=["audit"])


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
