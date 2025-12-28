"""
Request models for API validation
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class QueryRequest(BaseModel):
    """Request model for analytics query endpoint"""
    
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language analytics question"
    )
    
    shop_domain: str = Field(
        ...,
        description="Shopify shop domain (e.g., 'myshop.myshopify.com')"
    )
    
    access_token: str = Field(
        ...,
        description="Shopify access token for API authentication"
    )
    
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for query processing"
    )
    
    @validator("question")
    def validate_question(cls, v):
        """Validate question content"""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        v = " ".join(v.split())  # Remove excessive whitespace
        return v

    @validator("shop_domain")
    def validate_shop_domain(cls, v):
        """Validate shop domain format"""
        if not v or not v.strip():
            raise ValueError("Shop domain cannot be empty")
        
        v = v.strip().lower()
        
        # Allow demo domain
        if v == "demo.myshopify.com":
            return v
        
        # Ensure domain ends with myshopify.com
        if not v.endswith(".myshopify.com"):
            v = f"{v}.myshopify.com"
        
        return v

    @validator("access_token")
    def validate_access_token(cls, v):
        """Validate access token"""
        if not v or not v.strip():
            raise ValueError("Access token cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "question": "How many units of Blue T-Shirt will I need next month?",
                "shop_domain": "demo.myshopify.com",
                "access_token": "demo_token",
                "context": {
                    "timestamp": "2024-12-27T10:00:00Z"
                }
            }
        }
