"""
Configuration management using Pydantic BaseSettings.
Supports multiple environments (dev, staging, production).
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # ============== ENVIRONMENT ==============
    ENVIRONMENT: str = "development"  # development, staging, production

    # ============== BLOCKCHAIN ==============
    GANACHE_URL: str = "http://127.0.0.1:7545"
    CONTRACT_ADDRESS: Optional[str] = None
    PRIVATE_KEY: Optional[str] = None
    GAS_LIMIT: int = 3000000
    GAS_PRICE_GWEI: int = 20

    # ============== LOGGING ==============
    LOG_FILE: str = "logs/data.csv"
    LOG_LEVEL: str = "INFO"

    # ============== DETECTOR THRESHOLDS ==============
    HEART_RATE_MAX: int = 110
    TEMPERATURE_MAX: float = 38.0
    SPO2_MIN: int = 92

    # ============== SENSOR ==============
    SENSOR_INTERVAL_SEC: int = 5
    HEART_RATE_MIN: int = 60
    HEART_RATE_MAX_RANGE: int = 130
    TEMPERATURE_MIN: float = 36.0
    TEMPERATURE_MAX_RANGE: float = 39.5
    SPO2_MIN_RANGE: int = 88
    SPO2_MAX_RANGE: int = 100

    # ============== PATIENT ==============
    DEFAULT_PATIENT_ID: str = "P001"

    # ============== FEATURE FLAGS ==============
    ENABLE_BLOCKCHAIN: bool = True
    ENABLE_LOCAL_LOGGING: bool = True

    # ============== SUPABASE ==============
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    ENABLE_SUPABASE: bool = False

    # ============== CORS ==============
    # Comma-separated list, e.g. "https://app.vercel.app,https://mydomain.com"
    CORS_ALLOWED_ORIGINS: Optional[str] = None
    CORS_ALLOWED_ORIGIN_REGEX: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
