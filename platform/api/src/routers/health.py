"""
Health check endpoints
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..services.database import DatabaseService
from ..services.redis import RedisService


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]


@router.get("/", response_model=HealthResponse)
async def health_check(
    db: DatabaseService = Depends(),
    redis: RedisService = Depends()
) -> HealthResponse:
    """
    Comprehensive health check
    
    Returns:
        HealthResponse: Status of all services
    """
    services = {}
    
    # Check database
    try:
        await db.execute_query("SELECT 1")
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        await redis.ping()
        services["redis"] = "healthy"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)}"
    
    # Determine overall status
    overall_status = "healthy" if all(
        status == "healthy" for status in services.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="0.1.0",
        services=services
    )


@router.get("/ready")
async def readiness_check(
    db: DatabaseService = Depends(),
    redis: RedisService = Depends()
) -> Dict[str, Any]:
    """
    Kubernetes readiness probe
    
    Returns:
        Dict: Readiness status
    """
    try:
        # Check critical dependencies
        await db.execute_query("SELECT 1")
        await redis.ping()
        
        return {"status": "ready", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {str(e)}")


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe
    
    Returns:
        Dict: Liveness status
    """
    return {"status": "alive", "timestamp": datetime.utcnow()}
