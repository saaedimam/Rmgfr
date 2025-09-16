"""
Main FastAPI application for Anti-Fraud Platform
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Import routers
from .routers import events, decisions, cases, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sentry configuration
if os.getenv("SENTRY_DSN_API"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN_API"),
        integrations=[
            FastApiIntegration(auto_enabling_instrumentations=True),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Anti-Fraud Platform API")
    yield
    logger.info("Shutting down Anti-Fraud Platform API")


# Create FastAPI app
app = FastAPI(
    title="Anti-Fraud Platform API",
    description="High-performance fraud detection and prevention API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.vercel.app", "*.supabase.co"]
)

# Include routers
app.include_router(health.router)
app.include_router(events.router)
app.include_router(decisions.router)
app.include_router(cases.router)

# Pydantic models
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Error details")
    timestamp: str = Field(..., description="Error timestamp")


# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Anti-Fraud Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    import time
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"HTTP {exc.status_code} error",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    import time
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ).dict()
    )


if __name__ == "__main__":
    import time
    app.state.start_time = time.time()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
