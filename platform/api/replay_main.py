"""
Replay Worker Main Entry Point
Run with: uvicorn replay_main:app --reload --port 8082
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.services.replay_worker import replay_worker
from src.routers import replay

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Replay Worker")
    
    # Start the replay worker in background
    worker_task = asyncio.create_task(replay_worker.start_worker())
    
    yield
    
    # Cleanup
    logger.info("Stopping Replay Worker")
    await replay_worker.stop_worker()
    worker_task.cancel()

# Create FastAPI app
app = FastAPI(
    title="Replay Worker API",
    description="Event replay and reprocessing service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include replay router
app.include_router(replay.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "replay-worker",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
