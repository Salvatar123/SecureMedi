"""Emergency access service for break-glass workflows."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.supabase_service import SupabaseService
from config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EmergencyService:
    """Manage emergency access lifecycle and access checks."""

    def __init__(self):
        self.supabase: Optional[SupabaseService] = None
        self.use_supabase = False
        if settings.ENABLE_SUPABASE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.supabase = SupabaseService(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                self.use_supabase = self.supabase.emergency_table_available()
                if not self.use_supabase:
                    logger.warning("Emergency table missing; using local fallback storage")
            except Exception as exc:
                logger.warning(f"Supabase unavailable in emergency service: {exc}")

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        self.assignments_file = os.path.join(repo_root, "doctor_patient_assignments.json")
        self.sessions_file = os.path.join(repo_root, "logs", "emergency_sessions.json")
        os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)

    def _load_assignments(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.assignments_file):
            return {}
        try:
            with open(self.assignments_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _load_sessions(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.sessions_file):
            return {}
        try:
            with open(self.sessions_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_sessions(self, sessions: Dict[str, Dict[str, Any]]) -> None:
        with open(self.sessions_file, "w", encoding="utf-8") as handle:
            json.dump(sessions, handle, indent=2)

    def _expire_sessions(self, sessions: Dict[str, Dict[str, Any]]) -> bool:
        now = _utcnow()
        changed = False
        for session in sessions.values():
            if session.get("status") != "ACTIVE":
                continue
            expires_at = session.get("expires_at")
            if not expires_at:
                continue
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                if expires_dt.tzinfo is None:
                    expires_dt = expires_dt.replace(tzinfo=timezone.utc)
            except Exception:
                continue
            if expires_dt <= now:
                session["status"] = "EXPIRED"
                session["updated_at"] = now.isoformat()
                changed = True
        return changed

    def _doctor_exists(self, doctor_address: str) -> bool:
        if not self.supabase:
            return True
        doctor = self.supabase.get_doctor_by_address(doctor_address)
        return bool(doctor) and doctor.get("status", "active") != "inactive"

    def _patient_exists(self, patient_id: str) -> bool:
        if not self.supabase:
            return True
        patient = self.supabase.get_patient_by_id(patient_id)
        return bool(patient) and patient.get("status", "active") != "inactive"

    def is_doctor_assigned(self, doctor_address: str, patient_id: str) -> bool:
        """Return True if patient is assigned to this doctor in the local mapping."""
        if not self.supabase:
            return False

        try:
            doctor = self.supabase.get_doctor_by_address(doctor_address)
            patient = self.supabase.get_patient_by_id(patient_id)
            if not doctor or not patient:
                return False

            assignments = self._load_assignments()
            patient_db_id = str(patient.get("id"))
            assignment = assignments.get(patient_db_id)
            if not assignment:
                return False

            return str(assignment.get("doctor_id")) == str(doctor.get("id"))
        except Exception as exc:
            logger.warning(f"Failed to evaluate assignment for {doctor_address}/{patient_id}: {exc}")
            return False

    def create_session(
        self,
        doctor_address: str,
        patient_id: str,
        reason: str,
        severity: str,
        expected_duration_min: int,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        doctor_address_normalized = (doctor_address or "").strip().lower()
        patient_id_normalized = (patient_id or "").strip()

        if len((reason or "").strip()) < 15:
            raise ValueError("Reason must be at least 15 characters")

        severity_upper = (severity or "CRITICAL").upper()
        if severity_upper not in {"INFO", "WARNING", "CRITICAL"}:
            raise ValueError("Severity must be INFO, WARNING, or CRITICAL")

        if expected_duration_min < 5 or expected_duration_min > 120:
            raise ValueError("Expected duration must be between 5 and 120 minutes")

        if not self._doctor_exists(doctor_address_normalized):
            raise ValueError("Doctor does not exist or is inactive")

        if not self._patient_exists(patient_id_normalized):
            raise ValueError("Patient does not exist or is inactive")

        now = _utcnow()
        session_id = str(uuid4())
        session = {
            "id": session_id,
            "session_id": session_id,
            "doctor_address": doctor_address_normalized,
            "patient_id": patient_id_normalized,
            "reason": reason.strip(),
            "severity": severity_upper,
            "expected_duration_min": expected_duration_min,
            "status": "PENDING",
            "requested_at": now.isoformat(),
            "activated_at": None,
            "expires_at": None,
            "closed_at": None,
            "closure_note": None,
            "outcome": None,
            "activation_note": None,
            "blockchain_tx_hash": None,
            "created_ip": ip_address,
            "updated_at": now.isoformat(),
        }

        if self.use_supabase and self.supabase:
            expired_count = self.supabase.expire_stale_emergency_sessions()
            if expired_count:
                logger.info(f"Expired {expired_count} stale emergency sessions")

            active_same_case = self.supabase.get_active_emergency_sessions(
                doctor_address_normalized,
                patient_id_normalized,
            )
            if active_same_case:
                raise ValueError("An active emergency session already exists for this patient")

            result = self.supabase.create_emergency_session(session)
            if not result.get("success"):
                raise ValueError(result.get("error") or "Failed to create emergency session")
            return result.get("data") or session

        sessions = self._load_sessions()
        if self._expire_sessions(sessions):
            self._save_sessions(sessions)

        active_same_case = [
            s for s in sessions.values()
            if s.get("doctor_address", "").lower() == doctor_address_normalized
            and (s.get("patient_id") or "").strip() == patient_id_normalized
            and s.get("status") == "ACTIVE"
        ]
        if active_same_case:
            raise ValueError("An active emergency session already exists for this patient")

        sessions[session_id] = session
        self._save_sessions(sessions)
        return session

    def activate_session(
        self,
        session_id: str,
        doctor_address: str,
        activation_note: Optional[str] = None,
        blockchain_tx_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.use_supabase and self.supabase:
            self.supabase.expire_stale_emergency_sessions()
            session = self.supabase.get_emergency_session(session_id)
            if not session:
                raise ValueError("Emergency session not found")

            if session.get("doctor_address", "").lower() != doctor_address.lower():
                raise PermissionError("Only the requesting doctor can activate this session")

            if session.get("status") != "PENDING":
                raise ValueError("Only pending sessions can be activated")

            now = _utcnow()
            expires_at = now + timedelta(minutes=int(session.get("expected_duration_min", 30)))
            updates = {
                "status": "ACTIVE",
                "activated_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "activation_note": (activation_note or "").strip() or None,
                "blockchain_tx_hash": blockchain_tx_hash,
                "updated_at": now.isoformat(),
            }
            result = self.supabase.update_emergency_session(session_id, updates)
            if not result.get("success"):
                raise ValueError(result.get("error") or "Failed to activate emergency session")
            updated = result.get("data") or {**session, **updates}
            updated["session_id"] = updated.get("id", session_id)
            return updated

        sessions = self._load_sessions()
        if self._expire_sessions(sessions):
            self._save_sessions(sessions)

        session = sessions.get(session_id)
        if not session:
            raise ValueError("Emergency session not found")

        if session.get("doctor_address", "").lower() != doctor_address.lower():
            raise PermissionError("Only the requesting doctor can activate this session")

        if session.get("status") != "PENDING":
            raise ValueError("Only pending sessions can be activated")

        now = _utcnow()
        expires_at = now + timedelta(minutes=int(session.get("expected_duration_min", 30)))
        session["status"] = "ACTIVE"
        session["activated_at"] = now.isoformat()
        session["expires_at"] = expires_at.isoformat()
        session["activation_note"] = (activation_note or "").strip() or None
        session["blockchain_tx_hash"] = blockchain_tx_hash
        session["updated_at"] = now.isoformat()

        sessions[session_id] = session
        self._save_sessions(sessions)
        return session

    def close_session(
        self,
        session_id: str,
        actor_address: str,
        actor_role: str,
        closure_note: str,
        outcome: str,
    ) -> Dict[str, Any]:
        if self.use_supabase and self.supabase:
            self.supabase.expire_stale_emergency_sessions()
            session = self.supabase.get_emergency_session(session_id)
            if not session:
                raise ValueError("Emergency session not found")

            if actor_role != "ADMIN" and session.get("doctor_address", "").lower() != actor_address.lower():
                raise PermissionError("Only the owning doctor or admin can close this session")

            if session.get("status") not in {"ACTIVE", "EXPIRED"}:
                raise ValueError("Only active or expired sessions can be closed")

            if len((closure_note or "").strip()) < 8:
                raise ValueError("Closure note must be at least 8 characters")

            now = _utcnow()
            updates = {
                "status": "CLOSED",
                "closed_at": now.isoformat(),
                "closure_note": closure_note.strip(),
                "outcome": (outcome or "UNKNOWN").strip().upper(),
                "updated_at": now.isoformat(),
            }
            result = self.supabase.update_emergency_session(session_id, updates)
            if not result.get("success"):
                raise ValueError(result.get("error") or "Failed to close emergency session")
            updated = result.get("data") or {**session, **updates}
            updated["session_id"] = updated.get("id", session_id)
            return updated

        sessions = self._load_sessions()
        if self._expire_sessions(sessions):
            self._save_sessions(sessions)

        session = sessions.get(session_id)
        if not session:
            raise ValueError("Emergency session not found")

        if actor_role != "ADMIN" and session.get("doctor_address", "").lower() != actor_address.lower():
            raise PermissionError("Only the owning doctor or admin can close this session")

        if session.get("status") not in {"ACTIVE", "EXPIRED"}:
            raise ValueError("Only active or expired sessions can be closed")

        if len((closure_note or "").strip()) < 8:
            raise ValueError("Closure note must be at least 8 characters")

        now = _utcnow()
        session["status"] = "CLOSED"
        session["closed_at"] = now.isoformat()
        session["closure_note"] = closure_note.strip()
        session["outcome"] = (outcome or "UNKNOWN").strip().upper()
        session["updated_at"] = now.isoformat()

        sessions[session_id] = session
        self._save_sessions(sessions)
        return session

    def get_status(self, session_id: str) -> Dict[str, Any]:
        if self.use_supabase and self.supabase:
            self.supabase.expire_stale_emergency_sessions()
            session = self.supabase.get_emergency_session(session_id)
            if not session:
                raise ValueError("Emergency session not found")
            session["session_id"] = session.get("id", session_id)
        else:
            sessions = self._load_sessions()
            changed = self._expire_sessions(sessions)

            session = sessions.get(session_id)
            if not session:
                raise ValueError("Emergency session not found")

            if changed:
                self._save_sessions(sessions)

        now = _utcnow()
        seconds_remaining = 0
        if session.get("status") == "ACTIVE" and session.get("expires_at"):
            expires_dt = datetime.fromisoformat(session["expires_at"])
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=timezone.utc)
            seconds_remaining = max(0, int((expires_dt - now).total_seconds()))

        return {**session, "seconds_remaining": seconds_remaining}

    def has_active_access(self, doctor_address: str, patient_id: str) -> bool:
        """Break-glass authorization check used by patient/health endpoints."""
        if self.is_doctor_assigned(doctor_address, patient_id):
            return True

        if self.use_supabase and self.supabase:
            self.supabase.expire_stale_emergency_sessions()
            sessions = self.supabase.get_active_emergency_sessions(doctor_address, patient_id)
            return len(sessions) > 0

        sessions = self._load_sessions()
        changed = self._expire_sessions(sessions)
        if changed:
            self._save_sessions(sessions)

        for session in sessions.values():
            if (
                session.get("doctor_address", "").lower() == doctor_address.lower()
                and session.get("patient_id") == patient_id
                and session.get("status") == "ACTIVE"
            ):
                return True

        return False

    def has_active_emergency_session(self, doctor_address: str, patient_id: str) -> bool:
        """Return True only when an ACTIVE emergency session exists (ignores assignments)."""
        if self.use_supabase and self.supabase:
            self.supabase.expire_stale_emergency_sessions()
            sessions = self.supabase.get_active_emergency_sessions(doctor_address, patient_id)
            return len(sessions) > 0

        sessions = self._load_sessions()
        changed = self._expire_sessions(sessions)
        if changed:
            self._save_sessions(sessions)

        for session in sessions.values():
            if (
                session.get("doctor_address", "").lower() == doctor_address.lower()
                and session.get("patient_id") == patient_id
                and session.get("status") == "ACTIVE"
            ):
                return True

        return False

    def get_access_mode(self, doctor_address: str, patient_id: str) -> Optional[str]:
        """Resolve current access mode for doctor->patient read: EMERGENCY, NORMAL, or None."""
        if self.has_active_emergency_session(doctor_address, patient_id):
            return "EMERGENCY"
        if self.is_doctor_assigned(doctor_address, patient_id):
            return "NORMAL"
        return None

    def list_sessions(
        self,
        status: Optional[str] = None,
        doctor_address: Optional[str] = None,
        patient_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List emergency sessions for admin monitoring with optional filters."""
        normalized_status = status.upper() if status else None
        if normalized_status and normalized_status not in {"PENDING", "ACTIVE", "EXPIRED", "CLOSED", "REJECTED"}:
            raise ValueError("Invalid status filter")

        normalized_doctor = doctor_address.lower() if doctor_address else None
        normalized_patient = patient_id.strip() if patient_id else None

        if self.use_supabase and self.supabase:
            self.supabase.expire_stale_emergency_sessions()
            try:
                response = self.supabase.client.table(self.supabase.emergency_sessions_table).select("*").execute()
                rows = response.data or []
            except Exception as exc:
                raise ValueError(f"Failed to load emergency sessions from Supabase: {exc}")
        else:
            sessions = self._load_sessions()
            if self._expire_sessions(sessions):
                self._save_sessions(sessions)
            rows = list(sessions.values())

        filtered: List[Dict[str, Any]] = []
        for item in rows:
            item_status = (item.get("status") or "").upper()
            item_doctor = (item.get("doctor_address") or "").lower()
            item_patient = item.get("patient_id")

            if normalized_status and item_status != normalized_status:
                continue
            if normalized_doctor and item_doctor != normalized_doctor:
                continue
            if normalized_patient and item_patient != normalized_patient:
                continue

            normalized = dict(item)
            normalized["session_id"] = normalized.get("session_id") or normalized.get("id")
            filtered.append(normalized)

        def _latest_event_time(session: Dict[str, Any]) -> str:
            return (
                session.get("closed_at")
                or session.get("updated_at")
                or session.get("activated_at")
                or session.get("requested_at")
                or ""
            )

        filtered.sort(key=_latest_event_time, reverse=True)

        total = len(filtered)
        paginated = filtered[offset : offset + limit]

        return {
            "success": True,
            "data": paginated,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
