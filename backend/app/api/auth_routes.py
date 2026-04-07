"""Authentication Routes"""

from fastapi import APIRouter, HTTPException, status
from app.models.auth import LoginRequest, AuthResponse, UserRole
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()


@router.post("/login/doctor", response_model=AuthResponse)
async def login_doctor(request: LoginRequest):
    """Doctor login endpoint"""
    try:
        key_bytes = bytes.fromhex(request.key.replace("0x", ""))
        valid, message = auth_service.verify_doctor(request.address, key_bytes)
        
        if valid:
            token = auth_service.generate_access_token(request.address, UserRole.DOCTOR)
            return AuthResponse(
                success=True,
                token=token,
                role=UserRole.DOCTOR,
                user_address=request.address,
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
            token = auth_service.generate_access_token(request.address, UserRole.PATIENT)
            return AuthResponse(
                success=True,
                token=token,
                role=UserRole.PATIENT,
                user_address=request.address,
                message="Patient login successful"
            )
        else:
            return AuthResponse(success=False, message=message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
async def verify_token(token: str):
    """Verify token validity"""
    try:
        valid, address, role = auth_service.verify_token(token)
        return {"valid": valid, "address": address, "role": role}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(token: str):
    """Logout endpoint"""
    return {"message": "Logged out successfully"}
