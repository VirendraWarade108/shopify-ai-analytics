"""
Configuration management for AI Service
"""

from typing import List
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with Pydantic v2"""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields
        validate_assignment=True
    )

    # Application metadata
    APP_NAME: str = "Shopify Analytics AI Service"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Server configuration
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # Anthropic API configuration
    ANTHROPIC_API_KEY: str = Field(default="")
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-20250514")
    ANTHROPIC_MAX_TOKENS: int = Field(default=4096)
    ANTHROPIC_TEMPERATURE: float = Field(default=0.7)

    # Demo mode configuration
    DEMO_MODE: bool = Field(default=True)

    # Database (optional for demo mode)
    DATABASE_URL: str = Field(default="sqlite:///./demo.db")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Shopify API (optional for demo mode)
    SHOPIFY_API_KEY: str = Field(default="demo_key")
    SHOPIFY_API_SECRET: str = Field(default="demo_secret")
    SHOPIFY_SCOPES: str = Field(default="read_products,read_orders,read_analytics")

    # Security (optional for demo mode)
    LOCKBOX_MASTER_KEY: str = Field(default="demo_lockbox_key")
    SECRET_KEY_BASE: str = Field(default="demo_secret_base")

    # CORS configuration - using string to avoid parsing issues
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001"
    )

    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")

    # Forecasting configuration
    FORECAST_DAYS: int = Field(default=30, ge=1, le=365)
    HISTORICAL_DAYS: int = Field(default=90, ge=7, le=730)
    SAFETY_STOCK_MULTIPLIER: float = Field(default=1.2, ge=1.0, le=2.0)

    # Agent configuration
    AGENT_TIMEOUT: int = Field(default=120, ge=10, le=600)
    MAX_RETRIES: int = Field(default=3, ge=1, le=10)

    @field_validator("ANTHROPIC_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is between 0 and 1"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("ANTHROPIC_TEMPERATURE must be between 0 and 1")
        return v

    @field_validator("HISTORICAL_DAYS", "FORECAST_DAYS")
    @classmethod
    def validate_days(cls, v: int) -> int:
        """Validate day counts are positive"""
        if v < 1:
            raise ValueError("Days must be at least 1")
        return v
    
    def get_cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def validate_required_for_production(self) -> None:
        """Validate required settings for production"""
        if not self.DEMO_MODE:
            errors = []
            
            if not self.ANTHROPIC_API_KEY:
                errors.append("ANTHROPIC_API_KEY is required in production")
            
            if not self.SHOPIFY_API_KEY or self.SHOPIFY_API_KEY == "demo_key":
                errors.append("Valid SHOPIFY_API_KEY is required in production")
            
            if not self.SHOPIFY_API_SECRET or self.SHOPIFY_API_SECRET == "demo_secret":
                errors.append("Valid SHOPIFY_API_SECRET is required in production")
            
            if errors:
                raise ValueError(f"Production configuration errors: {', '.join(errors)}")


# Create global settings instance
settings = Settings()

# Validate production settings
if not settings.DEMO_MODE:
    settings.validate_required_for_production()
