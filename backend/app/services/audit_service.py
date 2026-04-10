"""Audit Service - Logs all sensitive operations for security audit trail"""

import logging
import json
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from enum import Enum
from dataclasses import asdict, dataclass

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Types of audit events"""
    # Authentication
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    TOKEN_REVOKE = "TOKEN_REVOKE"
    
    # Patient Data Access
    VIEW_PATIENT_DATA = "VIEW_PATIENT_DATA"
    VIEW_PATIENT_VITALS = "VIEW_PATIENT_VITALS"
    EXPORT_PATIENT_DATA = "EXPORT_PATIENT_DATA"
    
    # Doctor Operations
    VIEW_ACCESS_LOGS = "VIEW_ACCESS_LOGS"
    LOG_PATIENT_ACCESS = "LOG_PATIENT_ACCESS"
    GENERATE_ACCESS_KEY = "GENERATE_ACCESS_KEY"
    EMERGENCY_ACCESS = "EMERGENCY_ACCESS"
    
    # Admin Operations
    REGISTER_USER = "REGISTER_USER"
    UPDATE_USER_ROLE = "UPDATE_USER_ROLE"
    DEACTIVATE_USER = "DEACTIVATE_USER"
    VIEW_AUDIT_LOGS = "VIEW_AUDIT_LOGS"
    
    # System Events
    UNAUTHORIZED_ACCESS_ATTEMPT = "UNAUTHORIZED_ACCESS_ATTEMPT"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"


class AuditResult(str, Enum):
    """Result of audit event"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    DENIED = "DENIED"


@dataclass
class AuditLog:
    """Audit log entry"""
    timestamp: str
    actor_address: Optional[str]
    actor_role: Optional[str]
    action: str
    resource_id: Optional[str]
    resource_type: Optional[str]
    result: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    error_message: Optional[str] = None


class AuditService:
    """Service for audit logging and retrieval"""
    
    # In-memory audit log (will be moved to database in Phase 5)
    _audit_logs: List[AuditLog] = []
    _max_logs = 10000  # Limit to prevent memory bloat
    
    @classmethod
    def log_event(
        cls,
        action: AuditAction,
        actor_address: Optional[str] = None,
        actor_role: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        result: AuditResult = AuditResult.SUCCESS,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an audit event
        
        Args:
            action: Type of action (from AuditAction enum)
            actor_address: Who performed the action (user address)
            actor_role: Role of the actor (DOCTOR, PATIENT, ADMIN)
            resource_id: What resource was accessed (patient_id, user_address, etc.)
            resource_type: Type of resource (PATIENT_DATA, USER, etc.)
            result: Outcome of the action
            details: Additional context about the action
            ip_address: IP address of the request
            error_message: Error message if action failed
        
        Returns:
            AuditLog entry
        """
        log_entry = AuditLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_address=actor_address,
            actor_role=actor_role,
            action=action.value,
            resource_id=resource_id,
            resource_type=resource_type,
            result=result.value,
            details=details or {},
            ip_address=ip_address,
            error_message=error_message,
        )
        
        # Add to in-memory log
        cls._audit_logs.append(log_entry)
        
        # Trim old logs if exceeding limit
        if len(cls._audit_logs) > cls._max_logs:
            cls._audit_logs = cls._audit_logs[-cls._max_logs:]
        
        # Log to standard logger (structured)
        cls._log_structured(log_entry)
        
        # Log critical events to separate logger
        if action in [
            AuditAction.EMERGENCY_ACCESS,
            AuditAction.UNAUTHORIZED_ACCESS_ATTEMPT,
            AuditAction.DEACTIVATE_USER,
            AuditAction.UPDATE_USER_ROLE,
        ]:
            cls._log_critical(log_entry)
        
        return log_entry
    
    @classmethod
    def get_logs(
        cls,
        actor_address: Optional[str] = None,
        action: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[AuditLog], int]:
        """
        Retrieve audit logs with optional filtering
        
        Args:
            actor_address: Filter by actor (user who performed action)
            action: Filter by action type
            resource_id: Filter by resource accessed
            limit: Number of logs to return
            offset: Starting position
        
        Returns:
            Tuple of (filtered_logs, total_count)
        """
        # Filter logs
        filtered = cls._audit_logs
        
        if actor_address:
            filtered = [log for log in filtered if log.actor_address == actor_address]
        
        if action:
            filtered = [log for log in filtered if log.action == action]
        
        if resource_id:
            filtered = [log for log in filtered if log.resource_id == resource_id]
        
        # Sort by timestamp descending (newest first)
        filtered = sorted(filtered, key=lambda x: x.timestamp, reverse=True)
        
        total = len(filtered)
        
        # Apply pagination
        paginated = filtered[offset : offset + limit]
        
        return paginated, total
    
    @classmethod
    def get_user_activity(
        cls,
        user_address: str,
        limit: int = 50,
    ) -> List[AuditLog]:
        """Get all activity for a specific user"""
        logs, _ = cls.get_logs(actor_address=user_address, limit=limit)
        return logs
    
    @classmethod
    def get_resource_access(
        cls,
        resource_id: str,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get all access attempts for a specific resource"""
        logs, _ = cls.get_logs(resource_id=resource_id, limit=limit)
        return logs
    
    @classmethod
    def get_failed_attempts(cls, limit: int = 100) -> List[AuditLog]:
        """Get all failed/denied attempts (security issues)"""
        failed = [
            log for log in cls._audit_logs
            if log.result in [AuditResult.FAILURE.value, AuditResult.DENIED.value]
        ]
        # Sort by timestamp descending
        failed = sorted(failed, key=lambda x: x.timestamp, reverse=True)
        return failed[: limit]
    
    @classmethod
    def get_critical_events(cls, limit: int = 100) -> List[AuditLog]:
        """Get critical security events"""
        critical_actions = [
            AuditAction.EMERGENCY_ACCESS.value,
            AuditAction.UNAUTHORIZED_ACCESS_ATTEMPT.value,
            AuditAction.DEACTIVATE_USER.value,
            AuditAction.UPDATE_USER_ROLE.value,
        ]
        critical = [log for log in cls._audit_logs if log.action in critical_actions]
        critical = sorted(critical, key=lambda x: x.timestamp, reverse=True)
        return critical[:limit]
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get audit log statistics"""
        total_logs = len(cls._audit_logs)
        
        # Count by action
        action_counts = {}
        for log in cls._audit_logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
        
        # Count by result
        result_counts = {}
        for log in cls._audit_logs:
            result_counts[log.result] = result_counts.get(log.result, 0) + 1
        
        # Count unique users
        unique_users = len(set(log.actor_address for log in cls._audit_logs if log.actor_address))
        
        return {
            "total_logs": total_logs,
            "unique_users": unique_users,
            "action_counts": action_counts,
            "result_counts": result_counts,
        }
    
    @classmethod
    def _log_structured(cls, log_entry: AuditLog):
        """Log as structured JSON"""
        log_dict = asdict(log_entry)
        logger.info(json.dumps(log_dict, default=str))
    
    @classmethod
    def _log_critical(cls, log_entry: AuditLog):
        """Log critical events with higher visibility"""
        critical_logger = logging.getLogger("audit_critical")
        log_dict = asdict(log_entry)
        critical_logger.warning(json.dumps(log_dict, default=str))
    
    @classmethod
    def clear_logs(cls):
        """Clear all audit logs (for testing only)"""
        cls._audit_logs = []
