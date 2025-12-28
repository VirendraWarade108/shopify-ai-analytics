"""
Response models for API responses
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    """Response model for analytics query"""
    
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "intent": {
                    "domain": "inventory_forecasting",
                    "confidence": 0.92,
                    "entities": {
                        "product_name": "Blue T-Shirt",
                        "time_period": "next month"
                    }
                },
                "query": "FROM orders SHOW product_name, SUM(quantity) WHERE product_name = 'Blue T-Shirt'",
                "insights": {
                    "summary": "You'll need approximately 300 Blue T-Shirts next month",
                    "key_findings": [
                        "You sell about 8 Blue T-Shirts per day",
                        "Based on 90 days of sales history",
                        "Includes 50 units of safety stock"
                    ],
                    "recommendations": [
                        "Order 300 units to cover next month's demand",
                        "Monitor sales velocity weekly to adjust forecasts"
                    ],
                    "data_summary": {
                        "total_rows": 90,
                        "forecast_applied": True
                    }
                },
                "confidence": 0.88,
                "metadata": {
                    "shop_domain": "demo.myshopify.com",
                    "data_points": 90,
                    "forecast_applied": True
                }
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment name")
    demo_mode: bool = Field(..., description="Whether demo mode is enabled")
    checks: Dict[str, bool] = Field(..., description="Individual health checks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-12-27T10:00:00Z",
                "version": "1.0.0",
                "environment": "development",
                "demo_mode": True,
                "checks": {
                    "anthropic_api_key_configured": True
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response model for errors"""
    
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[Any] = Field(default=None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Validation error",
                "details": {
                    "field": "question",
                    "message": "Question cannot be empty"
                }
            }
        }