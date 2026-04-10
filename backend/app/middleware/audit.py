"""Audit Middleware - Captures and logs all API requests/responses"""

import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from datetime import datetime, timezone
import time

from app.services.audit_service import AuditService, AuditAction, AuditResult

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all API requests and responses for audit trail.
    
    Logs:
    - All protected endpoint accesses (authenticated users)
    - Request details (method, path, parameters)
    - Response status codes
    - Response times
    - Errors and exceptions
    """
    
    # Paths to audit (log all protected endpoints except health checks)
    AUDIT_PATHS = [
        "/api/health/",
        "/api/patients/",
        "/api/doctors/",
        "/api/admin/",
        "/api/auth/logout",
    ]
    
    # Paths that qualify as data access events
    SENSITIVE_ACTIONS = {
        ("GET", "/api/health/"): (AuditAction.VIEW_PATIENT_VITALS, "HEALTH_DATA"),
        ("GET", "/api/patients/"): (AuditAction.VIEW_PATIENT_DATA, "PATIENT_DATA"),
        ("POST", "/api/doctors/emergency/"): (AuditAction.EMERGENCY_ACCESS, "PATIENT_DATA"),
        ("POST", "/api/doctors/log-access"): (AuditAction.LOG_PATIENT_ACCESS, "ACCESS_LOG"),
        ("POST", "/api/doctors/generate-key"): (AuditAction.GENERATE_ACCESS_KEY, "ACCESS_KEY"),
    }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request, call handler, log activity"""
        
        # Only audit specific paths
        if not self._should_audit(request.url.path):
            return await call_next(request)
        
        # Extract request info
        request_time = time.time()
        method = request.method
        path = request.url.path
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get user info if authenticated
        user_info = getattr(request.state, "user", None)
        actor_address = user_info.get("address") if user_info else None
        actor_role = user_info.get("role") if user_info else None
        
        # Determine action type
        action, resource_type = self._determine_action(method, path)
        
        # Extract resource ID from path parameters
        resource_id = self._extract_resource_id(path)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - request_time
            
            # Determine result based on status code
            if 200 <= response.status_code < 300:
                result = AuditResult.SUCCESS
                error_msg = None
            elif response.status_code == 401:
                result = AuditResult.DENIED
                error_msg = "Unauthorized"
            elif response.status_code == 403:
                result = AuditResult.DENIED
                error_msg = "Forbidden"
            elif response.status_code == 400:
                result = AuditResult.FAILURE
                error_msg = "Bad Request"
            else:
                result = AuditResult.FAILURE
                error_msg = f"HTTP {response.status_code}"
            
            # Log the event
            details = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "response_time_ms": round(response_time * 1000, 2),
            }
            
            # Only log if there's a user context (not public endpoints)
            if actor_address:
                AuditService.log_event(
                    action=action,
                    actor_address=actor_address,
                    actor_role=actor_role,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    result=result,
                    details=details,
                    ip_address=client_ip,
                    error_message=error_msg,
                )
            
            return response
            
        except Exception as exc:
            # Log unexpected errors
            error_message = str(exc)
            
            if actor_address:
                AuditService.log_event(
                    action=action,
                    actor_address=actor_address,
                    actor_role=actor_role,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    result=AuditResult.FAILURE,
                    details={
                        "method": method,
                        "path": path,
                        "exception_type": type(exc).__name__,
                    },
                    ip_address=client_ip,
                    error_message=error_message,
                )
            
            logger.error(
                f"Error in {method} {path}: {error_message}",
                exc_info=True,
            )
            raise
    
    def _should_audit(self, path: str) -> bool:
        """Check if path should be audited"""
        for audit_path in self.AUDIT_PATHS:
            if path.startswith(audit_path):
                return True
        return False
    
    def _determine_action(self, method: str, path: str) -> tuple:
        """Determine audit action from method and path"""
        # Check sensitive actions map
        for (req_method, prefix), (action, resource_type) in self.SENSITIVE_ACTIONS.items():
            if method == req_method and path.startswith(prefix):
                return action, resource_type
        
        # Default actions based on path
        if "/api/health/" in path:
            return AuditAction.VIEW_PATIENT_VITALS, "HEALTH_DATA"
        elif "/api/patients/" in path:
            return AuditAction.VIEW_PATIENT_DATA, "PATIENT_DATA"
        elif "/api/doctors/" in path:
            return AuditAction.LOG_PATIENT_ACCESS, "ACCESS_LOG"
        elif "/api/admin/" in path:
            return AuditAction.VIEW_AUDIT_LOGS, "SYSTEM"
        elif "/api/auth/logout" in path:
            return AuditAction.LOGOUT, "SESSION"
        else:
            return AuditAction.LOG_PATIENT_ACCESS, "UNKNOWN"
    
    def _extract_resource_id(self, path: str) -> str:
        """Extract resource ID from path"""
        # Example: /api/patients/0x123abc -> 0x123abc
        parts = path.split("/")
        
        # Look for address-like patterns (0x followed by hex)
        for part in parts:
            if part.startswith("0x") and len(part) > 2:
                return part
        
        # Look for numeric IDs
        if len(parts) > 2 and parts[-1].isdigit():
            return parts[-1]
        
        # Return last non-empty part
        for part in reversed(parts):
            if part and not part.isdigit():
                return part
        
        return None
