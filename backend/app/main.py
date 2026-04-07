"""Main FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routes
from app.api import auth_routes, health_routes, patient_routes, doctor_routes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SecureMedi API",
    description="Secure Medical Data Platform - Backend API",
    version="2.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router)
app.include_router(health_routes.router)
app.include_router(patient_routes.router)
app.include_router(doctor_routes.router)


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
