"""
Anti-Fraud Platform API
FastAPI application with async support and comprehensive error handling
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


# Pydantic models
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    uptime: float = Field(..., description="Uptime in seconds")


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: str = Field(..., max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Item price")
    category: str = Field(..., min_length=1, max_length=50, description="Item category")


class ItemResponse(BaseModel):
    id: int = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    description: str = Field(..., description="Item description")
    price: float = Field(..., description="Item price")
    category: str = Field(..., description="Item category")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Error details")
    timestamp: str = Field(..., description="Error timestamp")


# In-memory storage for demo (replace with database)
items_db: Dict[int, Dict[str, Any]] = {}
next_id = 1


# Dependency for error handling
async def get_error_handler():
    """Dependency for consistent error handling"""
    return None


# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Anti-Fraud Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with performance metrics"""
    import time
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        uptime=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    )


@app.get("/items", response_model=list[ItemResponse])
async def get_items(skip: int = 0, limit: int = 100):
    """Get all items with pagination"""
    try:
        items = []
        for item_id, item_data in list(items_db.items())[skip:skip + limit]:
            items.append(ItemResponse(
                id=item_id,
                name=item_data["name"],
                description=item_data["description"],
                price=item_data["price"],
                category=item_data["category"],
                created_at=item_data["created_at"],
                updated_at=item_data["updated_at"]
            ))
        return items
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch items"
        )


@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item"""
    try:
        global next_id
        import time
        
        item_data = {
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "category": item.category,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        items_db[next_id] = item_data
        created_item = ItemResponse(
            id=next_id,
            **item_data
        )
        next_id += 1
        
        logger.info(f"Created item {next_id - 1}: {item.name}")
        return created_item
        
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create item"
        )


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get a specific item by ID"""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item_data = items_db[item_id]
    return ItemResponse(
        id=item_id,
        name=item_data["name"],
        description=item_data["description"],
        price=item_data["price"],
        category=item_data["category"],
        created_at=item_data["created_at"],
        updated_at=item_data["updated_at"]
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

