"""
Configuration management for AI Service
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application metadata
    APP_NAME: str = "Shopify Analytics AI Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Anthropic API configuration
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-20250514", env="ANTHROPIC_MODEL")
    ANTHROPIC_MAX_TOKENS: int = Field(default=4096, env="ANTHROPIC_MAX_TOKENS")
    ANTHROPIC_TEMPERATURE: float = Field(default=0.7, env="ANTHROPIC_TEMPERATURE")
    
    # Demo mode configuration
    DEMO_MODE: bool = Field(default=True, env="DEMO_MODE")
    
    # CORS configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Forecasting configuration
    FORECAST_DAYS: int = Field(default=30, env="FORECAST_DAYS")
    HISTORICAL_DAYS: int = Field(default=90, env="HISTORICAL_DAYS")
    SAFETY_STOCK_MULTIPLIER: float = Field(default=1.2, env="SAFETY_STOCK_MULTIPLIER")
    
    # Agent configuration
    AGENT_TIMEOUT: int = Field(default=120, env="AGENT_TIMEOUT")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Validation
def validate_settings():
    """Validate critical settings"""
    errors = []
    
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your_anthropic_api_key_here":
        errors.append("ANTHROPIC_API_KEY is not configured")
    
    if settings.ANTHROPIC_TEMPERATURE < 0 or settings.ANTHROPIC_TEMPERATURE > 1:
        errors.append("ANTHROPIC_TEMPERATURE must be between 0 and 1")
    
    if settings.FORECAST_DAYS < 1:
        errors.append("FORECAST_DAYS must be at least 1")
    
    if settings.HISTORICAL_DAYS < settings.FORECAST_DAYS:
        errors.append("HISTORICAL_DAYS should be greater than FORECAST_DAYS")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Run validation on import
try:
    validate_settings()
except ValueError as e:
    if not settings.DEMO_MODE:
        raise
    else:
        print(f"Warning: {e}")