"""
Anti-Fraud Platform API
FastAPI application with async PostgreSQL and Redis support
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from .routers import health, items
from .services.database import DatabaseService
from .services.redis import RedisService


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    supabase_url: str = "https://your-project.supabase.co"
    supabase_anon_key: str = "your-anon-key"
    supabase_db_url: str = "postgresql://postgres:password@db.your-project.supabase.co:5432/postgres"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    jwt_secret: str = "your-jwt-secret-min-32-chars"
    encryption_key: str = "your-encryption-key-32-chars"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 100
    
    # Sentry
    sentry_dsn: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()

# Initialize Sentry
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )

# Global services
db_service: DatabaseService | None = None
redis_service: RedisService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    global db_service, redis_service
    
    # Startup
    logging.info("Starting Anti-Fraud Platform API...")
    
    # Initialize database
    db_service = DatabaseService(settings.supabase_db_url)
    await db_service.connect()
    
    # Initialize Redis
    redis_service = RedisService(settings.redis_url)
    await redis_service.connect()
    
    logging.info("API startup complete")
    
    yield
    
    # Shutdown
    logging.info("Shutting down API...")
    
    if db_service:
        await db_service.disconnect()
    
    if redis_service:
        await redis_service.disconnect()
    
    logging.info("API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Anti-Fraud Platform API",
    description="Real-time fraud detection and prevention API",
    version="0.1.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-web.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.vercel.app", "*.vercel.com"]
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(items.router, prefix="/items", tags=["items"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Anti-Fraud Platform API",
        "version": "0.1.0",
        "status": "operational"
    }


# Dependency to get database service
async def get_db() -> DatabaseService:
    """Get database service dependency"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database not available")
    return db_service


# Dependency to get Redis service
async def get_redis() -> RedisService:
    """Get Redis service dependency"""
    if not redis_service:
        raise HTTPException(status_code=503, detail="Redis not available")
    return redis_service


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
