"""Main FastAPI Application"""

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from config.settings import get_settings

# Add backend to path to allow app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import routes
from app.api import auth_routes, health_routes, patient_routes, doctor_routes, admin_routes, audit_routes

# Import middleware
from app.middleware.auth import AuthenticationMiddleware
from app.middleware.audit import AuditMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


def _build_cors_origins() -> list[str]:
    default_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    configured = []
    if settings.CORS_ALLOWED_ORIGINS:
        configured = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
    # Preserve order while removing duplicates.
    seen = set()
    merged = []
    for origin in default_origins + configured:
        if origin not in seen:
            seen.add(origin)
            merged.append(origin)
    return merged

# Create FastAPI app
app = FastAPI(
    title="SecureMedi API",
    description="Secure Medical Data Platform - Backend API",
    version="2.0.0"
)

# CORS middleware for frontend communication (added first, executed last)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_cors_origins(),
    allow_origin_regex=(
        settings.CORS_ALLOWED_ORIGIN_REGEX
        or r"http://(localhost|127\.0\.0\.1|0\.0\.0\.0|169\.254\.[0-9]+\.[0-9]+)(:\d+)?"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit middleware (logs all requests/responses on protected endpoints)
app.add_middleware(AuditMiddleware)

# Authentication middleware (must be added before CORS, validates JWT tokens)
app.add_middleware(AuthenticationMiddleware)

# Include routes
app.include_router(auth_routes.router)
app.include_router(health_routes.router)
app.include_router(patient_routes.router)
app.include_router(doctor_routes.router)
app.include_router(admin_routes.router)
app.include_router(audit_routes.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SecureMedi API v2.0",
        "docs": "/docs",
        "health": "/api/health/vitals/latest"
    }


@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness check"""
    return {"status": "ready"}


@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness check"""
    return {"status": "alive"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
