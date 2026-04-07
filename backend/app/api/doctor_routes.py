"""Doctor Operations Routes"""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from app.models.doctor import DoctorInfo, AccessLog, EmergencyAccessRequest
from services.blockchain_service import BlockchainService

router = APIRouter(prefix="/api/doctors", tags=["doctors"])

blockchain_service = BlockchainService()


@router.get("/{doctor_address}", response_model=DoctorInfo)
async def get_doctor_info(doctor_address: str):
    """Get doctor information"""
    try:
        # TODO: Load from blockchain registry
        return DoctorInfo(address=doctor_address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doctor_address}/access-logs", response_model=List[AccessLog])
async def get_access_logs(doctor_address: str, limit: int = 100):
    """Get doctor's patient access logs"""
    try:
        # TODO: Load from blockchain
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doctor_address}/access-patient/{patient_id}")
async def log_patient_access(doctor_address: str, patient_id: str, access_type: str = "NORMAL", reason: str = ""):
    """Log doctor's access to patient record"""
    try:
        # TODO: Write to blockchain
        return {
            "success": True,
            "message": "Access logged",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{doctor_address}/generate-key")
async def generate_access_key(doctor_address: str):
    """Generate new access key for doctor"""
    try:
        # TODO: Generate and store in blockchain
        return {
            "success": True,
            "key": "0x" + "abcd1234" * 8,
            "message": "Access key generated"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emergency-access")
async def emergency_access(request: EmergencyAccessRequest):
    """Emergency access to patient data"""
    try:
        patient_data = blockchain_service.emergency_access(request.patient_id, request.key)
        return {
            "success": True,
            "message": "Emergency access granted",
            "patient_data": patient_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
