"""
Health check router
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from datetime import datetime
import time
from typing import Optional, Dict, Any

from ..services.database import get_database, DatabaseService

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    uptime: float = Field(..., description="Uptime in seconds")
    database: Optional[Dict[str, Any]] = Field(None, description="Database health status")

@router.get("/health", response_model=HealthResponse)
async def health_check(db: DatabaseService = Depends(get_database)):
    """Health check endpoint with performance metrics"""
    # Check database health
    db_health = None
    try:
        db_health = await db.health_check()
    except Exception as e:
        db_health = {"status": "error", "error": str(e)}
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        uptime=time.time() - getattr(health_check, 'start_time', time.time()),
        database=db_health
    )

@router.get("/health/database")
async def database_health_check(db: DatabaseService = Depends(get_database)):
    """Detailed database health check"""
    return await db.health_check()
