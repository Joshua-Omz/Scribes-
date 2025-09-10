"""Application configuration.

This module defines application settings from environment variables.
"""
import os
import sys
from typing import List, Union

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Check if we're running in a test environment
TESTING = "pytest" in sys.modules


class Settings(BaseSettings):
    """Application settings."""
    
    # Core settings
    APP_NAME: str = "Scribes"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "insecure-change-me-in-production"
    JWT_SECRET_KEY: str = "insecure-jwt-key-change-me"
    JWT_REFRESH_SECRET_KEY: str = "insecure-jwt-refresh-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: Union[str, PostgresDsn] = "postgresql://postgres:bbjbbjbbj371419@localhost:5432/scribes_db"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Environment
    TESTING: bool = TESTING
    
    # Configure settings based on environment
    model_config = SettingsConfigDict(
        env_file=None if TESTING else ".env",  # Don't load .env during tests
        case_sensitive=True,
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str) and v:
            return [origin.strip() for origin in v.split(",")]
        return v if v else ["*"]


# Create settings instance
settings = Settings()
