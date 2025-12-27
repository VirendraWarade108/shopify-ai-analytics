"""
Shopify Analytics AI Service
Main FastAPI application entry point
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config import settings
from models.requests import QueryRequest
from models.responses import QueryResponse, ErrorResponse, HealthResponse
from agent.orchestrator import AgentOrchestrator
from utils.logger import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("ai_service_starting", 
                version=settings.VERSION,
                environment=settings.ENVIRONMENT,
                demo_mode=settings.DEMO_MODE)
    
    # Verify Anthropic API key
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your_anthropic_api_key_here":
        logger.warning("anthropic_api_key_not_configured",
                      message="ANTHROPIC_API_KEY not set. Service will fail on actual requests.")
    
    yield
    
    # Shutdown
    logger.info("ai_service_shutting_down")


# Create FastAPI application
app = FastAPI(
    title="Shopify Analytics AI Service",
    description="AI-powered analytics query processing with 5-stage LLM agent pipeline",
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.error("validation_error",
                 path=request.url.path,
                 errors=exc.errors())
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error("unhandled_exception",
                 path=request.url.path,
                 error_type=type(exc).__name__,
                 error_message=str(exc),
                 exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    start_time = datetime.now()
    
    # Log request
    logger.info("request_started",
                method=request.method,
                path=request.url.path,
                client_host=request.client.host if request.client else None)
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    
    # Log response
    logger.info("request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2))
    
    return response


# Routes

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Shopify Analytics AI Service",
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "endpoints": {
            "health": "/health",
            "query": "/api/v1/query"
        },
        "llm_model": settings.ANTHROPIC_MODEL,
        "agent_pipeline": [
            "1. Intent Classification",
            "2. Query Planning",
            "3. ShopifyQL Generation",
            "4. Query Execution",
            "5. Insight Synthesis"
        ]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "checks": {
            "anthropic_api_key_configured": bool(
                settings.ANTHROPIC_API_KEY and 
                settings.ANTHROPIC_API_KEY != "your_anthropic_api_key_here"
            )
        }
    }
    
    return health_status


@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main endpoint for processing analytics questions
    
    This endpoint receives a natural language question and processes it through
    the 5-stage AI agent pipeline:
    1. Intent Classification
    2. Query Planning
    3. ShopifyQL Generation
    4. Query Execution
    5. Insight Synthesis
    """
    logger.info("query_received",
                question=request.question[:100],
                shop_domain=request.shop_domain,
                demo_mode=settings.DEMO_MODE)
    
    try:
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.ANTHROPIC_MODEL
        )
        
        # Process query through pipeline
        result = await orchestrator.process_query(
            question=request.question,
            shop_domain=request.shop_domain,
            access_token=request.access_token,
            context=request.context
        )
        
        logger.info("query_completed",
                    question=request.question[:100],
                    status=result.get("status"),
                    confidence=result.get("confidence"))
        
        return result
        
    except ValueError as e:
        logger.error("query_validation_error",
                    question=request.question[:100],
                    error=str(e))
        raise
        
    except Exception as e:
        logger.error("query_processing_error",
                    question=request.question[:100],
                    error_type=type(e).__name__,
                    error_message=str(e),
                    exc_info=True)
        
        return QueryResponse(
            status="failed",
            intent={},
            query="",
            insights={
                "summary": "Failed to process query",
                "key_findings": [],
                "recommendations": [],
                "data_summary": {}
            },
            confidence=0.0,
            error=str(e)
        )


# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )