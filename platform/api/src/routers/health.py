"""
Health check router
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
import time

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    uptime: float = Field(..., description="Uptime in seconds")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with performance metrics"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        uptime=time.time() - getattr(health_check, 'start_time', time.time())
    )