"""RBAC Middleware - Role-Based Access Control decorators"""

import logging
from functools import wraps
from typing import Callable, List, Optional
from fastapi import HTTPException, status, Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific roles for route access
    
    Usage:
        @app.get("/api/admin")
        @require_role("ADMIN")
        async def admin_endpoint(request: Request):
            pass
        
        @app.get("/api/patients")
        @require_role("DOCTOR", "PATIENT")
        async def get_patients(request: Request):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args or kwargs
            request = None
            if args:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                request = kwargs.get("request")
            
            if not request or not hasattr(request.state, "user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = request.state.user.get("role")
            if user_role not in allowed_roles:
                logger.warning(
                    f"Unauthorized access attempt - User {request.state.user.get('address')} "
                    f"({user_role}) tried to access endpoint requiring {allowed_roles}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_authenticated() -> Callable:
    """
    Decorator to require any authenticated user
    
    Usage:
        @app.get("/api/profile")
        @require_authenticated()
        async def get_profile(request: Request):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            if args:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                request = kwargs.get("request")
            
            if not request or not hasattr(request.state, "user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_self_or_role(*allowed_roles: str) -> Callable:
    """
    Decorator to allow either:
    1. Users accessing their own data (address matches)
    2. Users with specific roles
    
    Usage:
        @app.get("/api/patients/{patient_id}")
        @require_self_or_role("DOCTOR", "ADMIN")
        async def get_patient_data(patient_id: str, request: Request):
            # patient_id can be user's own address or a DOCTOR/ADMIN can access any
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            if args:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                request = kwargs.get("request")
            
            if not request or not hasattr(request.state, "user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_address = request.state.user.get("address")
            user_role = request.state.user.get("role")
            
            # Check if user has allowed role
            if user_role in allowed_roles:
                return await func(*args, **kwargs)
            
            # Check if accessing own data
            # Get the patient_id from kwargs
            target_id = kwargs.get("patient_id") or kwargs.get("address") or kwargs.get("user_id")
            
            if target_id and user_address == target_id:
                return await func(*args, **kwargs)
            
            logger.warning(
                f"Unauthorized access attempt - User {user_address} ({user_role}) "
                f"tried to access resource {target_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return wrapper
    return decorator


def get_current_user(request: Request) -> dict:
    """
    Helper function to get current user from request state
    
    Usage:
        @app.get("/api/profile")
        async def get_profile(request: Request):
            user = get_current_user(request)
            return {"address": user["address"], "role": user["role"]}
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return request.state.user
