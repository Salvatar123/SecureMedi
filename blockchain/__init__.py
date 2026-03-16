"""
Blockchain module - Web3 integration and smart contract interactions.
"""

from .connector import (
    generate_key,
    get_my_key,
    verify_key,
    log_access,
    register_doctor,
    is_doctor,
    register_patient,
    get_access_logs,
    get_access_logs_as_patient,
    generate_emergency_access,
)

__all__ = [
    "generate_key",
    "get_my_key",
    "verify_key",
    "log_access",
    "register_doctor",
    "is_doctor",
    "register_patient",
    "get_access_logs",
    "get_access_logs_as_patient",
    "generate_emergency_access",
]
