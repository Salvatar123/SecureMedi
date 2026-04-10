"""Authentication Routes"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from app.models.auth import LoginRequest, AuthResponse, UserRole, AccessKeyResponse, RefreshRequest
from app.services.auth_service import AuthService
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()


@router.post("/login/doctor", response_model=AuthResponse)
async def login_doctor(request: LoginRequest):
    """Doctor login endpoint"""
    try:
        valid, message = auth_service.verify_doctor(request.address, request.key)
        
        if valid:
            access_token = auth_service.generate_access_token(request.address, UserRole.DOCTOR)
            refresh_token = auth_service.generate_refresh_token(request.address, UserRole.DOCTOR)
            doctor_name = auth_service.get_doctor_name(request.address)
            return AuthResponse(
                success=True,
                token=access_token,
                refresh_token=refresh_token,
                role=UserRole.DOCTOR,
                user_address=request.address,
                user_name=doctor_name,
                message="Doctor login successful"
            )
        else:
            return AuthResponse(success=False, message=message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/patient", response_model=AuthResponse)
async def login_patient(request: LoginRequest):
    """Patient login endpoint"""
    try:
        valid, message = auth_service.verify_patient(request.address, request.key)
        
        if valid:
            access_token = auth_service.generate_access_token(request.address, UserRole.PATIENT)
            refresh_token = auth_service.generate_refresh_token(request.address, UserRole.PATIENT)
            patient_name = auth_service.get_patient_name(request.address)
            return AuthResponse(
                success=True,
                token=access_token,
                refresh_token=refresh_token,
                role=UserRole.PATIENT,
                user_address=request.address,
                user_name=patient_name,
                message="Patient login successful"
            )
        else:
            return AuthResponse(success=False, message=message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token"""
    try:
        is_valid, new_access_token, error = auth_service.refresh_access_token(request.refresh_token)
        
        if not is_valid:
            return AuthResponse(success=False, message=error)
        
        # Validate refresh token to get user info
        valid, payload, _ = auth_service.jwt_service.verify_token(request.refresh_token)
        if not valid:
            return AuthResponse(success=False, message="Invalid refresh token")
        
        user_address = payload.get("sub")
        role_str = payload.get("role")
        user_name = None
        if role_str == UserRole.DOCTOR.value and user_address:
            user_name = auth_service.get_doctor_name(user_address)
        elif role_str == UserRole.PATIENT.value and user_address:
            user_name = auth_service.get_patient_name(user_address)
        
        return AuthResponse(
            success=True,
            token=new_access_token,
            refresh_token=request.refresh_token,  # Return same refresh token
            role=UserRole(role_str) if role_str else None,
            user_address=user_address,
            user_name=user_name,
            message="Token refreshed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
async def verify_token(token: str):
    """Verify token validity"""
    try:
        is_valid, payload, error = auth_service.jwt_service.verify_token(token)
        if not is_valid:
            return {"valid": False, "error": error}
        
        return {
            "valid": True,
            "address": payload.get("sub"),
            "role": payload.get("role"),
            "expires_at": payload.get("exp")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Logout endpoint - revoke token"""
    try:
        if not authorization:
            return {"success": False, "message": "No token provided"}
        
        # Extract token from Bearer header
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        success, error = auth_service.logout(token)
        if success:
            return {"success": True, "message": "Logged out successfully"}
        else:
            return {"success": False, "message": error}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/request-key", response_model=AccessKeyResponse)
async def request_access_key():
    """Endpoint to request a new random access key."""
    try:
        key = auth_service.generate_random_key()
        return AccessKeyResponse(success=True, key=key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
