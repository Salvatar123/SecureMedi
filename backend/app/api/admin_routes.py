"""Admin Routes - User and system management endpoints"""

import logging
import json
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Request, Query, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.models.auth import UserRole
from app.middleware.rbac import require_role, get_current_user
from app.services.audit_service import AuditService, AuditAction, AuditResult
import sys
import os

# Add parent paths for Supabase import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from app.services.supabase_service import SupabaseService
from app.services.emergency_service import EmergencyService
from app.services.wallet_service import get_wallet_service
from config.settings import get_settings
try:
    from services.blockchain_service import BlockchainService
except ModuleNotFoundError:
    BlockchainService = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _is_duplicate_doctor_wallet_error(error_text: str) -> bool:
    """Return True when the error indicates a duplicate doctors.wallet_address constraint violation."""
    lowered = (error_text or "").lower()
    return (
        "doctors_wallet_address_key" in lowered
        or ("key (wallet_address)" in lowered and "already exists" in lowered)
        or "code': '23505" in lowered
        or 'code": "23505' in lowered
    )


def _unassign_wallet_by_address_all(wallet_service, address: Optional[str], user_type: str) -> int:
    """Remove all wallet assignment records that match an address and user type."""
    if not address:
        return 0

    removed = 0
    while wallet_service.unassign_wallet(address=address, user_type=user_type):
        removed += 1
    return removed


def _reconcile_orphan_wallet_assignments(wallet_service) -> int:
    """Remove wallet assignments that no longer map to existing doctor/patient records."""
    if not supabase_service:
        return 0

    try:
        doctors_response = supabase_service.client.table("doctors").select("wallet_address").execute()
        patients_response = supabase_service.client.table("patients").select("wallet_address").execute()

        valid_doctor_wallets = {
            (row.get("wallet_address") or "").lower()
            for row in (doctors_response.data or [])
            if row.get("wallet_address")
        }
        valid_patient_wallets = {
            (row.get("wallet_address") or "").lower()
            for row in (patients_response.data or [])
            if row.get("wallet_address")
        }

        removed = 0
        assigned = wallet_service.list_assigned_wallets() or {}
        for user_id, data in list(assigned.items()):
            user_type = str(data.get("user_type") or "").lower()
            address = (data.get("address") or "").lower()

            if not address or user_type not in {"doctor", "patient"}:
                continue

            if user_type == "doctor" and address not in valid_doctor_wallets:
                if wallet_service.unassign_wallet(user_id=user_id, address=address, user_type="doctor"):
                    removed += 1
            elif user_type == "patient" and address not in valid_patient_wallets:
                if wallet_service.unassign_wallet(user_id=user_id, address=address, user_type="patient"):
                    removed += 1

        return removed
    except Exception as e:
        logger.warning(f"Wallet reconciliation skipped due to error: {e}")
        return 0


class UserRegisterRequest(BaseModel):
    """Request to register a new user"""
    address: str = Field(..., description="Wallet address or patient ID")
    role: UserRole = Field(..., description="User role (DOCTOR, PATIENT)")
    name: Optional[str] = Field(None, description="User's full name")


class UserInfo(BaseModel):
    """User information"""
    address: str
    role: UserRole
    name: Optional[str] = None
    is_active: bool = True
    created_at: str


class UserListResponse(BaseModel):
    """Response with list of users"""
    success: bool
    users: List[UserInfo]
    total: int


class MessageResponse(BaseModel):
    """Standard message response"""
    success: bool
    message: str


class WalletResponse(BaseModel):
    """Wallet generation response"""
    success: bool
    wallet_address: Optional[str] = None
    private_key: Optional[str] = None
    message: str
    user_id: Optional[str] = None
    user_type: Optional[str] = None


class DoctorCreateRequest(BaseModel):
    """Request payload for creating a doctor"""
    name: str
    email: Optional[str] = None
    specialization: Optional[str] = None
    hospital: Optional[str] = None
    wallet_address: Optional[str] = None


class PatientCreateRequest(BaseModel):
    """Request payload for creating a patient"""
    patient_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    wallet_address: Optional[str] = None
    date_of_birth: Optional[str] = None
    emergency_contact: Optional[str] = None


class PatientDoctorAssignmentRequest(BaseModel):
    """Request payload for assigning a patient to a doctor"""
    patient_id: str
    doctor_id: Optional[str] = None


# In-memory user registry (will be moved to database in Phase 5)
USERS_DB = {}
ASSIGNMENTS_FILE = "doctor_patient_assignments.json"


def _load_patient_assignments() -> Dict[str, Dict[str, Any]]:
    """Load persisted patient-doctor assignments from file."""
    if os.path.exists(ASSIGNMENTS_FILE):
        try:
            with open(ASSIGNMENTS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.warning(f"Could not load patient assignments: {e}")
    return {}


def _save_patient_assignments(assignments: Dict[str, Dict[str, Any]]) -> None:
    """Persist patient-doctor assignments to file."""
    try:
        with open(ASSIGNMENTS_FILE, "w") as f:
            json.dump(assignments, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save patient assignments: {e}")


def _get_doctor_name_map() -> Dict[str, str]:
    """Fetch doctor ID to name mapping from Supabase."""
    if not supabase_service:
        return {}
    try:
        response = supabase_service.client.table("doctors").select("id,name").execute()
        return {str(doc.get("id")): doc.get("name", "") for doc in (response.data or [])}
    except Exception as e:
        logger.warning(f"Could not build doctor name map: {e}")
        return {}


@router.post("/users/register", response_model=MessageResponse)
@require_role("ADMIN")
async def register_user(request_data: UserRegisterRequest, request: Request):
    """
    Register a new user (Admin only)
    
    Only ADMIN role can register new users.
    """
    try:
        admin_user = get_current_user(request)
        logger.info(f"Admin {admin_user['address']} registering new {request_data.role} user")
        
        if request_data.address in USERS_DB:
            AuditService.log_event(
                action=AuditAction.REGISTER_USER,
                actor_address=admin_user['address'],
                actor_role=admin_user['role'],
                resource_id=request_data.address,
                resource_type="USER",
                result=AuditResult.FAILURE,
                error_message="User already registered",
            )
            return MessageResponse(
                success=False,
                message=f"User {request_data.address} already registered"
            )
        
        # Store user info
        USERS_DB[request_data.address] = {
            "address": request_data.address,
            "role": request_data.role.value,
            "name": request_data.name or "",
            "is_active": True,
            "created_at": "2024-01-01",  # Placeholder
            "created_by": admin_user["address"]
        }
        
        logger.info(f"User {request_data.address} registered with role {request_data.role}")
        
        AuditService.log_event(
            action=AuditAction.REGISTER_USER,
            actor_address=admin_user['address'],
            actor_role=admin_user['role'],
            resource_id=request_data.address,
            resource_type="USER",
            result=AuditResult.SUCCESS,
            details={"new_role": request_data.role.value, "user_name": request_data.name},
        )
        
        return MessageResponse(
            success=True,
            message=f"User {request_data.address} registered successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        admin_user = get_current_user(request)
        AuditService.log_event(
            action=AuditAction.REGISTER_USER,
            actor_address=admin_user['address'],
            actor_role=admin_user['role'],
            resource_id=request_data.address,
            resource_type="USER",
            result=AuditResult.FAILURE,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", response_model=UserListResponse)
@require_role("ADMIN")
async def list_users(request: Request):
    """List all registered users (Admin only)"""
    try:
        admin_user = get_current_user(request)
        logger.info(f"Admin {admin_user['address']} listing users")
        
        users = [
            UserInfo(
                address=user["address"],
                role=UserRole(user["role"]),
                name=user["name"],
                is_active=user["is_active"],
                created_at=user["created_at"]
            )
            for user in USERS_DB.values()
        ]
        
        return UserListResponse(
            success=True,
            users=users,
            total=len(users)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{address}", response_model=UserInfo)
@require_role("ADMIN")
async def get_user(address: str, request: Request):
    """Get user details (Admin only)"""
    try:
        admin_user = get_current_user(request)
        logger.info(f"Admin {admin_user['address']} accessing user {address} details")
        
        if address not in USERS_DB:
            raise HTTPException(
                status_code=404,
                detail=f"User {address} not found"
            )
        
        user = USERS_DB[address]
        return UserInfo(
            address=user["address"],
            role=UserRole(user["role"]),
            name=user["name"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/users/{address}/role", response_model=MessageResponse)
@require_role("ADMIN")
async def update_user_role(address: str, role: UserRole, request: Request):
    """Update user role (Admin only)"""
    try:
        admin_user = get_current_user(request)
        logger.info(f"Admin {admin_user['address']} updating {address} role to {role}")
        
        if address not in USERS_DB:
            AuditService.log_event(
                action=AuditAction.UPDATE_USER_ROLE,
                actor_address=admin_user['address'],
                actor_role=admin_user['role'],
                resource_id=address,
                resource_type="USER",
                result=AuditResult.FAILURE,
                error_message="User not found",
            )
            raise HTTPException(
                status_code=404,
                detail=f"User {address} not found"
            )
        
        old_role = USERS_DB[address]["role"]
        USERS_DB[address]["role"] = role.value
        
        logger.info(f"User {address} role updated from {old_role} to {role.value}")
        
        AuditService.log_event(
            action=AuditAction.UPDATE_USER_ROLE,
            actor_address=admin_user['address'],
            actor_role=admin_user['role'],
            resource_id=address,
            resource_type="USER",
            result=AuditResult.SUCCESS,
            details={"old_role": old_role, "new_role": role.value},
        )
        
        return MessageResponse(
            success=True,
            message=f"User {address} role updated to {role.value}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        admin_user = get_current_user(request)
        AuditService.log_event(
            action=AuditAction.UPDATE_USER_ROLE,
            actor_address=admin_user['address'],
            actor_role=admin_user['role'],
            resource_id=address,
            resource_type="USER",
            result=AuditResult.FAILURE,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{address}", response_model=MessageResponse)
@require_role("ADMIN")
async def deactivate_user(address: str, request: Request):
    """Deactivate user account (Admin only)"""
    try:
        admin_user = get_current_user(request)
        logger.info(f"Admin {admin_user['address']} deactivating user {address}")
        
        if address not in USERS_DB:
            AuditService.log_event(
                action=AuditAction.DEACTIVATE_USER,
                actor_address=admin_user['address'],
                actor_role=admin_user['role'],
                resource_id=address,
                resource_type="USER",
                result=AuditResult.FAILURE,
                error_message="User not found",
            )
            raise HTTPException(
                status_code=404,
                detail=f"User {address} not found"
            )
        
        # Prevent admin from deactivating themselves
        if admin_user["address"] == address:
            AuditService.log_event(
                action=AuditAction.DEACTIVATE_USER,
                actor_address=admin_user['address'],
                actor_role=admin_user['role'],
                resource_id=address,
                resource_type="USER",
                result=AuditResult.DENIED,
                error_message="Admin attempted self-deactivation",
            )
            return MessageResponse(
                success=False,
                message="Cannot deactivate your own account"
            )
        
        USERS_DB[address]["is_active"] = False
        logger.info(f"User {address} deactivated")
        
        AuditService.log_event(
            action=AuditAction.DEACTIVATE_USER,
            actor_address=admin_user['address'],
            actor_role=admin_user['role'],
            resource_id=address,
            resource_type="USER",
            result=AuditResult.SUCCESS,
        )
        
        return MessageResponse(
            success=True,
            message=f"User {address} deactivated"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user: {e}")
        admin_user = get_current_user(request)
        AuditService.log_event(
            action=AuditAction.DEACTIVATE_USER,
            actor_address=admin_user['address'],
            actor_role=admin_user['role'],
            resource_id=address,
            resource_type="USER",
            result=AuditResult.FAILURE,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
@require_role("ADMIN")
async def get_admin_stats(request: Request):
    """Get system statistics (Admin only)"""
    try:
        admin_user = get_current_user(request)
        logger.info(f"Admin {admin_user['address']} requesting system stats")
        
        # Count users by role
        role_counts = {}
        for user in USERS_DB.values():
            role = user["role"]
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "success": True,
            "total_users": len(USERS_DB),
            "active_users": sum(1 for u in USERS_DB.values() if u["is_active"]),
            "users_by_role": role_counts
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SUPABASE DEPENDENCIES ====================

# Initialize Supabase service
settings = get_settings()
supabase_service = None

if settings.ENABLE_SUPABASE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        supabase_service = SupabaseService(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase service initialized for admin routes")
    except Exception as e:
        logger.warning(f"Supabase not available: {e}")

    emergency_service = EmergencyService()

# ==================== BLOCKCHAIN DEPENDENCIES ====================

# Initialize blockchain service
blockchain_service = None

try:
    blockchain_service = BlockchainService() if BlockchainService else None
    logger.info("Blockchain service initialized for admin routes")
except Exception as e:
    logger.warning(f"Blockchain service not available: {e}")


# ==================== WALLET GENERATION ====================

@router.post("/wallets/generate", response_model=WalletResponse)
@require_role("ADMIN")
async def generate_wallet(
    user_id: str,
    user_type: str = "doctor",
    request: Request = None
):
    """Generate a wallet for a doctor or patient"""
    try:
        admin_user = get_current_user(request) if request else {"address": "system"}
        logger.info(f"Admin {admin_user.get('address')} generating wallet for {user_type} {user_id}")
        
        wallet_service = get_wallet_service()
        wallet_address, private_key, error = wallet_service.generate_wallet(user_id, user_type)
        
        if error and wallet_address is None:
            logger.error(f"Failed to generate wallet: {error}")
            return WalletResponse(
                success=False,
                message=error,
                user_id=user_id,
                user_type=user_type
            )
        
        # If already assigned, return just the address (not the private key again)
        if error and wallet_address:
            return WalletResponse(
                success=True,
                wallet_address=wallet_address,
                message=error,  # "User already has a wallet assigned"
                user_id=user_id,
                user_type=user_type,
                private_key=None  # Don't return private key for security
            )
        
        AuditService.log_event(
            action=AuditAction.REGISTER_USER,
            actor_address=admin_user.get('address'),
            actor_role="ADMIN",
            resource_id=user_id,
            resource_type=f"WALLET_{user_type.upper()}",
            result=AuditResult.SUCCESS,
            details={"wallet_address": wallet_address}
        )
        
        return WalletResponse(
            success=True,
            wallet_address=wallet_address,
            private_key=private_key,
            message=f"Wallet generated for {user_type} {user_id}",
            user_id=user_id,
            user_type=user_type
        )
    except Exception as e:
        logger.error(f"Error generating wallet: {e}")
        return WalletResponse(
            success=False,
            message=f"Error generating wallet: {str(e)}",
            user_id=user_id,
            user_type=user_type
        )


@router.get("/wallets/available")
async def get_available_wallets(request: Request = None):
    """Get available Ganache accounts (Public endpoint for testing)"""
    try:
        wallet_service = get_wallet_service()
        orphan_removed_count = _reconcile_orphan_wallet_assignments(wallet_service)
        assigned = wallet_service.list_assigned_wallets()
        available = wallet_service.get_available_count()
        total = wallet_service.get_total_count()

        db_doctor_wallet_count = 0
        db_patient_wallet_count = 0
        db_in_use_wallet_count = 0
        if supabase_service:
            try:
                doctors_response = supabase_service.client.table("doctors").select("wallet_address").execute()
                patients_response = supabase_service.client.table("patients").select("wallet_address").execute()

                doctor_wallets = {
                    (row.get("wallet_address") or "").lower()
                    for row in (doctors_response.data or [])
                    if row.get("wallet_address")
                }
                patient_wallets = {
                    (row.get("wallet_address") or "").lower()
                    for row in (patients_response.data or [])
                    if row.get("wallet_address")
                }

                db_doctor_wallet_count = len(doctor_wallets)
                db_patient_wallet_count = len(patient_wallets)
                db_in_use_wallet_count = len(doctor_wallets.union(patient_wallets))
            except Exception as e:
                logger.warning(f"Unable to compute DB wallet usage counts: {e}")
        
        return {
            "success": True,
            "total_accounts": total,
            "assigned_count": len(assigned),
            "available_count": available,
            "orphan_removed_count": orphan_removed_count,
            "db_doctor_wallet_count": db_doctor_wallet_count,
            "db_patient_wallet_count": db_patient_wallet_count,
            "db_in_use_wallet_count": db_in_use_wallet_count,
            "assigned_wallets": [
                {
                    "user_id": user_id,
                    "user_type": data.get("user_type"),
                    "address": data.get("address"),
                    "account_index": data.get("account_index"),
                    "assigned_at": data.get("assigned_at")
                }
                for user_id, data in assigned.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error getting available wallets: {e}", exc_info=True)
        return {"success": False, "message": str(e)}


def get_supabase_service():
    """Dependency to get Supabase service"""
    if not supabase_service:
        raise HTTPException(
            status_code=503,
            detail="Supabase service not available. Check SUPABASE_URL and SUPABASE_KEY in environment."
        )
    return supabase_service


@router.get("/emergency/sessions")
@require_role("ADMIN")
async def list_emergency_sessions(
    status: Optional[str] = Query(default=None),
    doctor_address: Optional[str] = Query(default=None),
    patient_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    request: Request = None,
):
    """List emergency access sessions for admin monitoring and review."""
    try:
        admin_user = get_current_user(request)
        result = emergency_service.list_sessions(
            status=status,
            doctor_address=doctor_address,
            patient_id=patient_id,
            limit=limit,
            offset=offset,
        )

        AuditService.log_event(
            action=AuditAction.VIEW_AUDIT_LOGS,
            actor_address=admin_user["address"],
            actor_role=admin_user["role"],
            resource_id="emergency_sessions",
            resource_type="EMERGENCY_SESSION",
            result=AuditResult.SUCCESS,
            details={
                "status": status,
                "doctor_address": doctor_address,
                "patient_id": patient_id,
                "limit": limit,
                "offset": offset,
            },
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing emergency sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emergency/debug-status")
@require_role("ADMIN")
async def get_emergency_debug_status(request: Request):
    """Return emergency service storage diagnostics (Supabase vs fallback)."""
    try:
        admin_user = get_current_user(request)

        settings_state = {
            "ENABLE_SUPABASE": bool(settings.ENABLE_SUPABASE),
            "SUPABASE_URL_SET": bool(settings.SUPABASE_URL),
            "SUPABASE_KEY_SET": bool(settings.SUPABASE_KEY),
        }

        emergency_state = {
            "service_initialized": emergency_service is not None,
            "using_supabase": bool(getattr(emergency_service, "use_supabase", False)),
            "has_supabase_client": bool(getattr(emergency_service, "supabase", None)),
            "sessions_file": getattr(emergency_service, "sessions_file", None),
            "local_sessions_file_exists": False,
            "local_sessions_count": 0,
            "supabase_table": "emergency_access_sessions",
            "supabase_table_accessible": False,
        }

        sessions_file = emergency_state["sessions_file"]
        if sessions_file:
            emergency_state["local_sessions_file_exists"] = os.path.exists(sessions_file)

        if emergency_service and hasattr(emergency_service, "_load_sessions"):
            try:
                local_sessions = emergency_service._load_sessions()  # diagnostics only
                emergency_state["local_sessions_count"] = len(local_sessions or {})
            except Exception:
                emergency_state["local_sessions_count"] = -1

        if emergency_service and getattr(emergency_service, "supabase", None):
            try:
                emergency_state["supabase_table_accessible"] = emergency_service.supabase.emergency_table_available()
            except Exception:
                emergency_state["supabase_table_accessible"] = False

        AuditService.log_event(
            action=AuditAction.VIEW_AUDIT_LOGS,
            actor_address=admin_user["address"],
            actor_role=admin_user["role"],
            resource_id="emergency_debug_status",
            resource_type="SYSTEM",
            result=AuditResult.SUCCESS,
            details={
                "using_supabase": emergency_state["using_supabase"],
                "supabase_table_accessible": emergency_state["supabase_table_accessible"],
            },
        )

        return {
            "success": True,
            "settings": settings_state,
            "emergency_service": emergency_state,
        }
    except Exception as e:
        logger.error(f"Error fetching emergency debug status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCTORS MANAGEMENT ====================

@router.get("/registry/doctors")
async def list_doctors(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    request: Request = None
):
    """List all doctors with pagination (Public endpoint for testing)"""
    try:
        logger.info("Listing doctors")
        
        # If Supabase is not available, return empty list for testing
        if not supabase_service:
            logger.warning("Supabase not available, returning mock data for testing")
            return {
                "success": True,
                "data": [],
                "total": 0,
                "message": "Supabase not configured - returning empty list"
            }
        
        result = supabase_service.get_all_doctors(limit=limit, offset=offset)
        if not result.get("success"):
            logger.error(f"Failed to fetch doctors: {result.get('error')}")
            return {
                "success": False,
                "data": [],
                "error": result.get("error", "Failed to fetch doctors")
            }
        
        return result
    except Exception as e:
        logger.error(f"Error listing doctors: {e}", exc_info=True)
        return {
            "success": False,
            "data": [],
            "error": str(e)
        }


@router.get("/registry/doctors/{doctor_id}/wallet")
async def get_doctor_wallet(doctor_id: str, request: Request = None):
    """Get wallet details for a specific doctor (Public endpoint for testing)"""
    try:
        if not supabase_service:
            return {
                "success": False,
                "message": "Supabase not configured. Wallet lookup is unavailable.",
            }

        doctor_result = (
            supabase_service.client
            .table("doctors")
            .select("id,name,email,wallet_address")
            .eq("id", doctor_id)
            .limit(1)
            .execute()
        )

        if not doctor_result.data:
            return {
                "success": False,
                "message": "Doctor not found",
            }

        doctor = doctor_result.data[0]
        wallet_address = (doctor.get("wallet_address") or "").lower()
        doctor_email = doctor.get("email")

        wallet_service = get_wallet_service()
        assigned_wallets = wallet_service.list_assigned_wallets()

        wallet_data = None

        # Preferred match by email/user_id if available.
        if doctor_email and doctor_email in assigned_wallets:
            wallet_data = assigned_wallets.get(doctor_email)

        # Fallback to matching by wallet address.
        if wallet_data is None and wallet_address:
            for _, details in assigned_wallets.items():
                if (details.get("address") or "").lower() == wallet_address:
                    wallet_data = details
                    break

        return {
            "success": True,
            "doctor": {
                "id": doctor.get("id"),
                "name": doctor.get("name"),
                "email": doctor_email,
            },
            "wallet": {
                "address": wallet_data.get("address") if wallet_data else doctor.get("wallet_address"),
                "private_key": wallet_data.get("private_key") if wallet_data else None,
                "account_index": wallet_data.get("account_index") if wallet_data else None,
                "assigned_at": wallet_data.get("assigned_at") if wallet_data else None,
                "user_type": wallet_data.get("user_type") if wallet_data else "doctor",
            },
            "message": "Wallet details loaded" if wallet_data else "Wallet address found, private key not available in local assignment store",
        }
    except Exception as e:
        logger.error(f"Error getting doctor wallet: {e}", exc_info=True)
        return {
            "success": False,
            "message": str(e),
        }


@router.get("/registry/doctors/search")
@require_role("ADMIN")
async def search_doctors(
    q: str = Query(..., min_length=1),
    request: Request = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """Search doctors by name, email, specialization, or wallet address"""
    try:
        admin_user = get_current_user(request) if request else {"address": "system"}
        logger.info(f"Admin {admin_user.get('address')} searching doctors: {q}")
        
        result = service.search_doctors(q)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to search doctors"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching doctors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/registry/doctors")
async def create_doctor(
    payload: DoctorCreateRequest,
    request: Request = None,
):
    """Create a new doctor"""
    try:
        admin_user = get_current_user(request) if request and hasattr(request.state, "user") else {"address": "system"}
        name = payload.name
        email = payload.email
        specialization = payload.specialization
        hospital = payload.hospital
        wallet_address = payload.wallet_address

        logger.info(f"Admin {admin_user.get('address')} creating doctor: {name}")

        if not supabase_service:
            return {
                "success": False,
                "message": "Supabase not configured. Doctor creation is unavailable until SUPABASE_URL and SUPABASE_KEY are set.",
            }
        
        # Auto-generate wallet if not provided. Retry a few times if generated wallet
        # collides with an existing DB record.
        private_key = None
        generated_wallet = not wallet_address
        wallet_service = get_wallet_service() if generated_wallet else None
        seed_user_id = (email or f"doctor_{name.replace(' ', '_')}").strip() if generated_wallet else ""
        wallet_user_id = seed_user_id
        result = None

        for attempt in range(5):
            if generated_wallet:
                wallet_address, private_key, error = wallet_service.generate_wallet(wallet_user_id, "doctor")
                if not wallet_address:
                    raise HTTPException(status_code=400, detail=f"Failed to generate wallet: {error}")

                # Existing wallet assignment for same seed (for example repeated email) can
                # re-use an old address. Move to a unique assignment key and retry.
                if error and "already has a wallet assigned" in str(error).lower():
                    wallet_user_id = f"{seed_user_id}_{uuid4().hex[:8]}"
                    continue

            result = supabase_service.add_doctor(
                wallet_address=wallet_address,
                name=name,
                email=email,
                specialization=specialization,
                hospital=hospital
            )

            if result.get("success"):
                break

            error_text = result.get("error", "Failed to create doctor in database")
            if generated_wallet and _is_duplicate_doctor_wallet_error(error_text):
                wallet_service.unassign_wallet(user_id=wallet_user_id, user_type="doctor")
                wallet_user_id = f"{seed_user_id}_{uuid4().hex[:8]}"
                wallet_address = None
                private_key = None
                continue

            raise HTTPException(status_code=400, detail=error_text)

        if not result or not result.get("success"):
            raise HTTPException(status_code=400, detail="Failed to create doctor after retrying wallet assignment")
        
        # Second, register on blockchain
        blockchain_error = None
        if blockchain_service:
            try:
                blockchain_service.register_doctor(wallet_address)
                logger.info(f"Doctor {wallet_address} registered on blockchain")
            except Exception as e:
                logger.error(f"Failed to register doctor on blockchain: {e}")
                blockchain_error = str(e)
        
        AuditService.log_event(
            action=AuditAction.REGISTER_USER,
            actor_address=admin_user.get('address'),
            actor_role="ADMIN",
            resource_id=wallet_address,
            resource_type="DOCTOR",
            result=AuditResult.SUCCESS,
            details={"name": name, "specialization": specialization, "blockchain_status": "success" if not blockchain_error else f"warning: {blockchain_error}"}
        )
        
        response = result.copy() if isinstance(result, dict) else {"success": True}
        response["wallet_address"] = wallet_address
        if private_key:
            response["private_key"] = private_key
            response["credentials_message"] = "IMPORTANT: Save the private key securely. It will not be shown again."
        if blockchain_error:
            response["blockchain_warning"] = f"Doctor added to database but blockchain registration had an issue: {blockchain_error}"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/registry/doctors/{doctor_id}")
@require_role("ADMIN")
async def update_doctor(
    doctor_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    specialization: Optional[str] = None,
    hospital: Optional[str] = None,
    status: Optional[str] = None,
    request: Request = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """Update doctor information"""
    try:
        admin_user = get_current_user(request) if request else {"address": "system"}
        logger.info(f"Admin {admin_user.get('address')} updating doctor: {doctor_id}")
        
        updates = {}
        if name is not None:
            updates["name"] = name
        if email is not None:
            updates["email"] = email
        if specialization is not None:
            updates["specialization"] = specialization
        if hospital is not None:
            updates["hospital"] = hospital
        if status is not None:
            updates["status"] = status
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = service.update_doctor(doctor_id, **updates)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update doctor"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating doctor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/registry/doctors/{doctor_id}")
async def delete_doctor(
    doctor_id: str,
    request: Request = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """Delete a doctor"""
    try:
        admin_user = (
            get_current_user(request)
            if request and hasattr(request.state, "user")
            else {"address": "system"}
        )
        logger.info(f"Admin {admin_user.get('address')} deleting doctor: {doctor_id}")

        doctor = service.get_doctor_by_id(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        result = service.delete_doctor(doctor_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete doctor"))

        wallet_service = get_wallet_service()
        wallet_unassigned = wallet_service.unassign_wallet(
            user_id=doctor.get("email"),
            address=doctor.get("wallet_address"),
            user_type="doctor",
        )
        extra_unassigned = _unassign_wallet_by_address_all(
            wallet_service,
            doctor.get("wallet_address"),
            "doctor",
        )

        result["wallet_unassigned"] = wallet_unassigned
        result["wallet_unassigned_count"] = (1 if wallet_unassigned else 0) + extra_unassigned
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting doctor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/doctors/export/csv")
async def export_doctors_csv(
    request: Request = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """Export all doctors as CSV (Public endpoint for testing)"""
    try:
        admin_user = get_current_user(request) if request and hasattr(request.state, "user") else {"address": "system"}
        logger.info(f"Admin {admin_user.get('address')} exporting doctors")
        
        csv_content = service.export_doctors_csv()
        if not csv_content:
            raise HTTPException(status_code=500, detail="Failed to export doctors")
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=doctors_export.csv"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting doctors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PATIENTS MANAGEMENT ====================

@router.get("/registry/patients")
async def list_patients(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    request: Request = None
):
    """List all patients with pagination (Public endpoint for testing)"""
    try:
        logger.info("Listing patients")

        if not supabase_service:
            logger.warning("Supabase not available, returning mock patient data for testing")
            return {
                "success": True,
                "data": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "message": "Supabase not configured - returning empty list"
            }
        
        result = supabase_service.get_all_patients(limit=limit, offset=offset)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to fetch patients"))

        assignments = _load_patient_assignments()
        doctor_name_map = _get_doctor_name_map()
        for patient in result.get("data", []):
            pid = str(patient.get("id"))
            assignment = assignments.get(pid)
            patient["assigned_doctor_id"] = assignment.get("doctor_id") if assignment else None
            patient["assigned_doctor_name"] = doctor_name_map.get(assignment.get("doctor_id"), "") if assignment else None

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/patients/{patient_id}/wallet")
async def get_patient_wallet(patient_id: str, request: Request = None):
    """Get wallet details for a specific patient (Public endpoint for testing)."""
    try:
        if not supabase_service:
            return {
                "success": False,
                "message": "Supabase not configured. Wallet lookup is unavailable.",
            }

        patient_result = (
            supabase_service.client
            .table("patients")
            .select("id,patient_id,name,email,wallet_address")
            .eq("id", patient_id)
            .limit(1)
            .execute()
        )

        if not patient_result.data:
            return {
                "success": False,
                "message": "Patient not found",
            }

        patient = patient_result.data[0]
        patient_registry_id = patient.get("patient_id")
        patient_email = patient.get("email")
        wallet_address = (patient.get("wallet_address") or "").lower()

        wallet_service = get_wallet_service()
        assigned_wallets = wallet_service.list_assigned_wallets()

        wallet_data = None

        # Preferred match by patient_id (wallet user_id during creation flow).
        if patient_registry_id and patient_registry_id in assigned_wallets:
            wallet_data = assigned_wallets.get(patient_registry_id)

        # Fallback by email.
        if wallet_data is None and patient_email and patient_email in assigned_wallets:
            wallet_data = assigned_wallets.get(patient_email)

        # Fallback by wallet address.
        if wallet_data is None and wallet_address:
            for _, details in assigned_wallets.items():
                if (details.get("address") or "").lower() == wallet_address:
                    wallet_data = details
                    break

        return {
            "success": True,
            "patient": {
                "id": patient.get("id"),
                "patient_id": patient_registry_id,
                "name": patient.get("name"),
                "email": patient_email,
            },
            "wallet": {
                "address": wallet_data.get("address") if wallet_data else patient.get("wallet_address"),
                "private_key": wallet_data.get("private_key") if wallet_data else None,
                "account_index": wallet_data.get("account_index") if wallet_data else None,
                "assigned_at": wallet_data.get("assigned_at") if wallet_data else None,
                "user_type": wallet_data.get("user_type") if wallet_data else "patient",
            },
            "message": "Wallet details loaded" if wallet_data else "Wallet address found, private key not available in local assignment store",
        }
    except Exception as e:
        logger.error(f"Error getting patient wallet: {e}", exc_info=True)
        return {
            "success": False,
            "message": str(e),
        }


@router.get("/registry/assignments")
async def list_patient_doctor_assignments(request: Request = None):
    """List all persisted patient-doctor assignments (Public endpoint for testing)."""
    try:
        assignments = _load_patient_assignments()
        return {
            "success": True,
            "data": assignments,
        }
    except Exception as e:
        logger.error(f"Error listing assignments: {e}", exc_info=True)
        return {
            "success": False,
            "message": str(e),
            "data": {},
        }


@router.post("/registry/assignments")
async def assign_patient_to_doctor(payload: PatientDoctorAssignmentRequest, request: Request = None):
    """Assign or unassign a patient to/from a doctor (Public endpoint for testing)."""
    try:
        actor = get_current_user(request) if request and hasattr(request.state, "user") else {"address": "system"}

        if not supabase_service:
            return {
                "success": False,
                "message": "Supabase not configured. Assignment is unavailable.",
            }

        patient_id = (payload.patient_id or "").strip()
        doctor_id = (payload.doctor_id or "").strip() or None

        if not patient_id:
            return {
                "success": False,
                "message": "patient_id is required",
            }

        patient_lookup = (
            supabase_service.client
            .table("patients")
            .select("id,patient_id,name")
            .eq("id", patient_id)
            .limit(1)
            .execute()
        )
        if not patient_lookup.data:
            return {
                "success": False,
                "message": "Patient not found",
            }

        assignments = _load_patient_assignments()

        if doctor_id is None:
            assignments.pop(patient_id, None)
            _save_patient_assignments(assignments)
            return {
                "success": True,
                "message": "Patient unassigned successfully",
                "patient_id": patient_id,
                "doctor_id": None,
            }

        doctor_lookup = (
            supabase_service.client
            .table("doctors")
            .select("id,name")
            .eq("id", doctor_id)
            .limit(1)
            .execute()
        )
        if not doctor_lookup.data:
            return {
                "success": False,
                "message": "Doctor not found",
            }

        doctor = doctor_lookup.data[0]
        assignments[patient_id] = {
            "doctor_id": doctor_id,
            "assigned_at": str(__import__("datetime").datetime.utcnow().isoformat()),
            "assigned_by": actor.get("address", "system"),
        }
        _save_patient_assignments(assignments)

        return {
            "success": True,
            "message": "Patient assigned successfully",
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "doctor_name": doctor.get("name"),
        }
    except Exception as e:
        logger.error(f"Error assigning patient to doctor: {e}", exc_info=True)
        return {
            "success": False,
            "message": str(e),
        }


@router.get("/registry/patients/search")
async def search_patients(
    q: str = Query(..., min_length=1),
    request: Request = None
):
    """Search patients by name, email, or patient ID (Public endpoint for testing)"""
    try:
        logger.info(f"Searching patients: {q}")

        if not supabase_service:
            logger.warning("Supabase not available, returning empty search results for testing")
            return {
                "success": True,
                "data": [],
                "message": "Supabase not configured - returning empty results"
            }
        
        result = supabase_service.search_patients(q)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to search patients"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/registry/patients")
async def create_patient(
    payload: PatientCreateRequest,
    request: Request = None
):
    """Create a new patient"""
    try:
        admin_user = get_current_user(request) if request and hasattr(request.state, "user") else {"address": "system"}
        patient_id = payload.patient_id
        name = payload.name
        email = payload.email
        wallet_address = payload.wallet_address
        date_of_birth = payload.date_of_birth
        emergency_contact = payload.emergency_contact

        logger.info(f"Admin {admin_user.get('address')} creating patient: {patient_id}")

        if not supabase_service:
            return {
                "success": False,
                "message": "Supabase not configured. Patient creation is unavailable until SUPABASE_URL and SUPABASE_KEY are set.",
            }
        
        # Auto-generate wallet if not provided
        private_key = None
        if not wallet_address:
            wallet_service = get_wallet_service()
            wallet_address, private_key, error = wallet_service.generate_wallet(patient_id, "patient")
            
            if not wallet_address:
                raise HTTPException(status_code=400, detail=f"Failed to generate wallet: {error}")
        
        # First, add to Supabase
        result = supabase_service.add_patient(
            patient_id=patient_id,
            wallet_address=wallet_address,
            name=name,
            email=email,
            date_of_birth=date_of_birth,
            emergency_contact=emergency_contact
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create patient in database"))
        
        # Second, register on blockchain
        blockchain_error = None
        if blockchain_service and wallet_address:
            try:
                blockchain_service.register_patient(patient_id, wallet_address)
                logger.info(f"Patient {patient_id} registered on blockchain")
            except Exception as e:
                logger.error(f"Failed to register patient on blockchain: {e}")
                blockchain_error = str(e)
        
        AuditService.log_event(
            action=AuditAction.REGISTER_USER,
            actor_address=admin_user.get('address'),
            actor_role="ADMIN",
            resource_id=patient_id,
            resource_type="PATIENT",
            result=AuditResult.SUCCESS,
            details={"name": name, "email": email, "blockchain_status": "success" if not blockchain_error else f"warning: {blockchain_error}"}
        )
        
        response = result.copy() if isinstance(result, dict) else {"success": True}
        response["wallet_address"] = wallet_address
        if private_key:
            response["private_key"] = private_key
            response["credentials_message"] = "IMPORTANT: Save the private key securely. It will not be shown again."
        if blockchain_error:
            response["blockchain_warning"] = f"Patient added to database but blockchain registration had an issue: {blockchain_error}"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/registry/patients/{patient_id}")
@require_role("ADMIN")
async def update_patient(
    patient_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    wallet_address: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    emergency_contact: Optional[str] = None,
    status: Optional[str] = None,
    request: Request = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """Update patient information"""
    try:
        admin_user = get_current_user(request) if request else {"address": "system"}
        logger.info(f"Admin {admin_user.get('address')} updating patient: {patient_id}")
        
        updates = {}
        if name is not None:
            updates["name"] = name
        if email is not None:
            updates["email"] = email
        if wallet_address is not None:
            updates["wallet_address"] = wallet_address.lower()
        if date_of_birth is not None:
            updates["date_of_birth"] = date_of_birth
        if emergency_contact is not None:
            updates["emergency_contact"] = emergency_contact
        if status is not None:
            updates["status"] = status
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = service.update_patient(patient_id, **updates)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update patient"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/registry/patients/{patient_id}")
async def delete_patient(
    patient_id: str,
    request: Request = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """Delete a patient"""
    try:
        admin_user = (
            get_current_user(request)
            if request and hasattr(request.state, "user")
            else {"address": "system"}
        )
        logger.info(f"Admin {admin_user.get('address')} deleting patient: {patient_id}")

        patient = service.get_patient_by_db_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        result = service.delete_patient(patient_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete patient"))

        wallet_service = get_wallet_service()
        wallet_unassigned = wallet_service.unassign_wallet(
            user_id=patient.get("patient_id") or patient.get("email"),
            address=patient.get("wallet_address"),
            user_type="patient",
        )

        result["wallet_unassigned"] = wallet_unassigned
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/patients/export/csv")
async def export_patients_csv(
    request: Request = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """Export all patients as CSV (Public endpoint for testing)"""
    try:
        admin_user = get_current_user(request) if request and hasattr(request.state, "user") else {"address": "system"}
        logger.info(f"Admin {admin_user.get('address')} exporting patients")
        
        csv_content = service.export_patients_csv()
        if not csv_content:
            raise HTTPException(status_code=500, detail="Failed to export patients")
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=patients_export.csv"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))
