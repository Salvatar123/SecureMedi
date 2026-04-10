"""Authentication Middleware - Validates JWT tokens on protected routes"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate JWT tokens from Authorization header"""
    
    # Routes that don't require authentication
    UNAUTHENTICATED_ROUTES = {
        "/api/auth/login/doctor",
        "/api/auth/login/patient",
        "/api/auth/refresh",
        "/api/auth/request-key",
        "/api/admin/wallets/available",
        "/api/admin/registry/doctors",
        "/api/admin/registry/doctors/export/csv",
        "/api/admin/registry/patients",
        "/api/admin/registry/patients/search",
        "/api/admin/registry/patients/export/csv",
        "/api/admin/registry/assignments",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate token if required"""
        if request.method.upper() == "OPTIONS":
            return await call_next(request)

        normalized_path = request.url.path.rstrip("/") or "/"

        is_public_doctor_wallet_route = (
            normalized_path.startswith("/api/admin/registry/doctors/")
            and normalized_path.endswith("/wallet")
        )

        is_public_patient_wallet_route = (
            normalized_path.startswith("/api/admin/registry/patients/")
            and normalized_path.endswith("/wallet")
        )
        
        # Skip authentication for public routes
        if normalized_path in self.UNAUTHENTICATED_ROUTES or is_public_doctor_wallet_route or is_public_patient_wallet_route:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        token = self._extract_token(auth_header)
        
        # Routes that require authentication
        if normalized_path.startswith("/api/"):
            if not token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing Authorization header"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Validate token
            try:
                from app.services.jwt_service import JWTService
                jwt_service = JWTService()
                is_valid, payload, error = jwt_service.verify_token(token)
                
                if not is_valid:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": error or "Invalid or expired token"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Attach user info to request state for use in routes
                request.state.user = {
                    "address": payload.get("sub"),
                    "role": payload.get("role"),
                    "token_type": payload.get("type"),
                    "expires_at": payload.get("exp"),
                    "jti": payload.get("jti"),
                }
                
                logger.debug(f"User {payload.get('sub')} ({payload.get('role')}) authenticated")
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Token validation error: {e}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token validation failed"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        response = await call_next(request)
        return response
    
    @staticmethod
    def _extract_token(auth_header: Optional[str]) -> Optional[str]:
        """Extract token from Authorization header"""
        if not auth_header:
            return None
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
