"""
Response models for API responses
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class QueryResponse(BaseModel):
    """Response model for analytics query"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "intent": {
                    "domain": "inventory_forecasting",
                    "confidence": 0.92
                },
                "query": "FROM orders SHOW product_name, SUM(quantity)",
                "insights": {
                    "summary": "You'll need approximately 300 Blue T-Shirts next month",
                    "key_findings": [
                        "You sell about 8 Blue T-Shirts per day"
                    ]
                },
                "confidence": 0.88
            }
        }
    )
    
    status: str = Field(
        ...,
        description="Query status: 'completed', 'failed', 'processing'"
    )
    
    intent: Dict[str, Any] = Field(
        ...,
        description="Classified intent with domain and confidence"
    )
    
    query: str = Field(
        ...,
        description="Generated ShopifyQL query"
    )
    
    insights: Dict[str, Any] = Field(
        ...,
        description="Business-friendly insights"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0 to 1.0)"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about query execution"
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Error message if query failed"
    )


class HealthResponse(BaseModel):
    """Response model for health check"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-12-27T10:00:00Z",
                "version": "2.0.0"
            }
        }
    )
    
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment name")
    demo_mode: bool = Field(..., description="Whether demo mode is enabled")
    checks: Dict[str, bool] = Field(..., description="Individual health checks")


class ErrorResponse(BaseModel):
    """Response model for errors"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "Validation error"
            }
        }
    )
    
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[Any] = Field(default=None, description="Additional error details")