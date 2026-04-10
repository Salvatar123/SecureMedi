"""
Supabase Service - Manages database operations for doctors and patients
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for Supabase database operations"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        self.client: Client = create_client(supabase_url, supabase_key)
        self.doctors_table = "doctors"
        self.patients_table = "patients"
        self.emergency_sessions_table = "emergency_access_sessions"
    
    # ===================== DOCTORS =====================
    
    def add_doctor(self, wallet_address: str, name: str, email: Optional[str] = None,
                   specialization: Optional[str] = None, hospital: Optional[str] = None) -> Dict[str, Any]:
        """Add a new doctor to the database"""
        try:
            data = {
                "wallet_address": wallet_address.lower(),
                "name": name,
                "email": email,
                "specialization": specialization,
                "hospital": hospital,
                "status": "active",
                "registered_on": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.doctors_table).insert(data).execute()
            logger.info(f"Doctor added: {wallet_address}")
            return {"success": True, "data": response.data[0] if response.data else data}
        except Exception as e:
            logger.error(f"Error adding doctor: {e}")
            return {"success": False, "error": str(e)}
    
    def get_doctor_by_address(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get doctor by wallet address"""
        try:
            response = self.client.table(self.doctors_table) \
                .select("*") \
                .eq("wallet_address", wallet_address.lower()) \
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting doctor: {e}")
            return None
    
    def get_all_doctors(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get all doctors with pagination"""
        try:
            response = self.client.table(self.doctors_table) \
                .select("*") \
                .order("registered_on", desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            
            # Get total count
            count_response = self.client.table(self.doctors_table).select("*", count="exact").execute()
            
            return {
                "success": True,
                "data": response.data,
                "total": count_response.count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error getting all doctors: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    def search_doctors(self, query: str) -> Dict[str, Any]:
        """Search doctors by name, email, or specialization"""
        try:
            response = self.client.table(self.doctors_table) \
                .select("*") \
                .execute()
            
            # Client-side filtering
            results = [
                doc for doc in response.data
                if query.lower() in doc.get("name", "").lower()
                or query.lower() in doc.get("email", "").lower()
                or query.lower() in doc.get("specialization", "").lower()
                or query.lower() in doc.get("wallet_address", "").lower()
            ]
            
            return {"success": True, "data": results}
        except Exception as e:
            logger.error(f"Error searching doctors: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    def update_doctor(self, doctor_id: str, **kwargs) -> Dict[str, Any]:
        """Update doctor information"""
        try:
            response = self.client.table(self.doctors_table) \
                .update(kwargs) \
                .eq("id", doctor_id) \
                .execute()
            
            logger.info(f"Doctor updated: {doctor_id}")
            return {"success": True, "data": response.data[0] if response.data else kwargs}
        except Exception as e:
            logger.error(f"Error updating doctor: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_doctor(self, doctor_id: str) -> Dict[str, Any]:
        """Delete a doctor"""
        try:
            response = self.client.table(self.doctors_table) \
                .delete() \
                .eq("id", doctor_id) \
                .execute()
            
            logger.info(f"Doctor deleted: {doctor_id}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Error deleting doctor: {e}")
            return {"success": False, "error": str(e)}
    
    def export_doctors_csv(self) -> Optional[str]:
        """Export all doctors as CSV"""
        try:
            response = self.client.table(self.doctors_table) \
                .select("*") \
                .execute()
            
            doctors = response.data
            if not doctors:
                return None
            
            # Create CSV header
            csv_lines = [",".join(doctors[0].keys())]
            
            # Add doctor records
            for doc in doctors:
                row = [str(doc.get(key, "")).replace(",", ";") for key in doctors[0].keys()]
                csv_lines.append(",".join(row))
            
            return "\n".join(csv_lines)
        except Exception as e:
            logger.error(f"Error exporting doctors: {e}")
            return None
    
    # ===================== PATIENTS =====================
    
    def add_patient(self, patient_id: str, wallet_address: Optional[str] = None,
                    name: Optional[str] = None, email: Optional[str] = None,
                    date_of_birth: Optional[str] = None, emergency_contact: Optional[str] = None) -> Dict[str, Any]:
        """Add a new patient to the database"""
        try:
            data = {
                "patient_id": patient_id,
                "wallet_address": wallet_address.lower() if wallet_address else None,
                "name": name,
                "email": email,
                "date_of_birth": date_of_birth,
                "emergency_contact": emergency_contact,
                "status": "active",
                "registered_on": datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.patients_table).insert(data).execute()
            logger.info(f"Patient added: {patient_id}")
            return {"success": True, "data": response.data[0] if response.data else data}
        except Exception as e:
            logger.error(f"Error adding patient: {e}")
            return {"success": False, "error": str(e)}
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by patient ID"""
        try:
            response = self.client.table(self.patients_table) \
                .select("*") \
                .eq("patient_id", patient_id) \
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting patient: {e}")
            return None
    
    def get_all_patients(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get all patients with pagination"""
        try:
            response = self.client.table(self.patients_table) \
                .select("*") \
                .order("registered_on", desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            
            # Get total count
            count_response = self.client.table(self.patients_table).select("*", count="exact").execute()
            
            return {
                "success": True,
                "data": response.data,
                "total": count_response.count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error getting all patients: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    def search_patients(self, query: str) -> Dict[str, Any]:
        """Search patients by name, email, or patient ID"""
        try:
            response = self.client.table(self.patients_table) \
                .select("*") \
                .execute()
            
            # Client-side filtering
            results = [
                pat for pat in response.data
                if query.lower() in pat.get("patient_id", "").lower()
                or query.lower() in pat.get("name", "").lower()
                or query.lower() in pat.get("email", "").lower()
                or query.lower() in pat.get("wallet_address", "").lower()
            ]
            
            return {"success": True, "data": results}
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    def update_patient(self, patient_id: str, **kwargs) -> Dict[str, Any]:
        """Update patient information"""
        try:
            response = self.client.table(self.patients_table) \
                .update(kwargs) \
                .eq("id", patient_id) \
                .execute()
            
            logger.info(f"Patient updated: {patient_id}")
            return {"success": True, "data": response.data[0] if response.data else kwargs}
        except Exception as e:
            logger.error(f"Error updating patient: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_patient(self, patient_id: str) -> Dict[str, Any]:
        """Delete a patient"""
        try:
            response = self.client.table(self.patients_table) \
                .delete() \
                .eq("id", patient_id) \
                .execute()
            
            logger.info(f"Patient deleted: {patient_id}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Error deleting patient: {e}")
            return {"success": False, "error": str(e)}
    
    def export_patients_csv(self) -> Optional[str]:
        """Export all patients as CSV"""
        try:
            response = self.client.table(self.patients_table) \
                .select("*") \
                .execute()
            
            patients = response.data
            if not patients:
                return None
            
            # Create CSV header
            csv_lines = [",".join(patients[0].keys())]
            
            # Add patient records
            for pat in patients:
                row = [str(pat.get(key, "")).replace(",", ";") for key in patients[0].keys()]
                csv_lines.append(",".join(row))
            
            return "\n".join(csv_lines)
        except Exception as e:
            logger.error(f"Error exporting patients: {e}")
            return None

    # ===================== EMERGENCY SESSIONS =====================

    def emergency_table_available(self) -> bool:
        """Check whether emergency session table exists and is queryable."""
        try:
            self.client.table(self.emergency_sessions_table).select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.warning(f"Emergency table unavailable: {e}")
            return False

    def create_emergency_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new emergency session row."""
        try:
            response = self.client.table(self.emergency_sessions_table).insert(session_data).execute()
            row = response.data[0] if response.data else session_data
            return {"success": True, "data": row}
        except Exception as e:
            logger.error(f"Error creating emergency session: {e}")
            return {"success": False, "error": str(e)}

    def get_emergency_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get emergency session by id."""
        try:
            response = (
                self.client
                .table(self.emergency_sessions_table)
                .select("*")
                .eq("id", session_id)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error reading emergency session {session_id}: {e}")
            return None

    def update_emergency_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Patch emergency session row and return updated record."""
        try:
            response = (
                self.client
                .table(self.emergency_sessions_table)
                .update(updates)
                .eq("id", session_id)
                .execute()
            )
            row = response.data[0] if response.data else updates
            return {"success": True, "data": row}
        except Exception as e:
            logger.error(f"Error updating emergency session {session_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_active_emergency_sessions(self, doctor_address: str, patient_id: str) -> List[Dict[str, Any]]:
        """Return active emergency sessions for doctor+patient pair."""
        try:
            now_iso = datetime.utcnow().isoformat()
            response = (
                self.client
                .table(self.emergency_sessions_table)
                .select("*")
                .eq("doctor_address", doctor_address)
                .eq("patient_id", patient_id)
                .eq("status", "ACTIVE")
                .gt("expires_at", now_iso)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error querying active emergency sessions: {e}")
            return []

    def expire_stale_emergency_sessions(self) -> int:
        """Mark ACTIVE sessions as EXPIRED when their expiry has passed."""
        try:
            now_iso = datetime.utcnow().isoformat()
            response = (
                self.client
                .table(self.emergency_sessions_table)
                .select("id")
                .eq("status", "ACTIVE")
                .lte("expires_at", now_iso)
                .execute()
            )
            stale = response.data or []
            for row in stale:
                self.client.table(self.emergency_sessions_table).update(
                    {"status": "EXPIRED", "updated_at": now_iso}
                ).eq("id", row.get("id")).execute()
            return len(stale)
        except Exception as e:
            logger.error(f"Error expiring emergency sessions: {e}")
            return 0
