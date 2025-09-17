"""
Replay API router for event replay management
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime

from ..services.replay_worker import replay_worker, ReplayStatus

router = APIRouter(prefix="/v1/replay", tags=["replay"])

class ReplayRequest(BaseModel):
    event_ids: List[str] = Field(..., description="List of event IDs to replay")
    schema_version: int = Field(..., description="Schema version for replay")
    reason: str = Field(..., description="Reason for replay (e.g., 'rule_change:rule_42@v7')")

class ReplayResponse(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: str

class JobStatusResponse(BaseModel):
    id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    processed_count: int
    total_count: int
    error_message: Optional[str] = None

class JobListResponse(BaseModel):
    jobs: List[JobStatusResponse]
    total: int

@router.post("/enqueue", response_model=ReplayResponse, status_code=status.HTTP_201_CREATED)
async def enqueue_replay(request: ReplayRequest):
    """
    Enqueue a new replay job
    """
    try:
        job_id = await replay_worker.enqueue_replay(
            event_ids=request.event_ids,
            schema_version=request.schema_version,
            reason=request.reason
        )
        
        return ReplayResponse(
            job_id=job_id,
            status="pending",
            message=f"Replay job {job_id} enqueued with {len(request.event_ids)} events",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue replay job: {str(e)}"
        )

@router.post("/run_once")
async def run_once(limit: int = Query(100, description="Maximum number of events to process")):
    """
    Process one batch of replay jobs
    """
    try:
        result = await replay_worker.run_once(limit=limit)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process replay jobs: {str(e)}"
        )

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a specific replay job
    """
    try:
        job_status = await replay_worker.get_job_status(job_id)
        if not job_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return JobStatusResponse(**job_status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )

@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(status: Optional[str] = Query(None, description="Filter by status")):
    """
    List all replay jobs
    """
    try:
        # Convert string status to enum if provided
        status_filter = None
        if status:
            try:
                status_filter = ReplayStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}. Valid values: {[s.value for s in ReplayStatus]}"
                )
        
        jobs = await replay_worker.list_jobs(status=status_filter)
        
        return JobListResponse(
            jobs=[JobStatusResponse(**job) for job in jobs],
            total=len(jobs)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )

@router.post("/worker/start")
async def start_worker():
    """
    Start the replay worker
    """
    try:
        await replay_worker.start_worker()
        return {"message": "Replay worker started"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start worker: {str(e)}"
        )

@router.post("/worker/stop")
async def stop_worker():
    """
    Stop the replay worker
    """
    try:
        await replay_worker.stop_worker()
        return {"message": "Replay worker stopped"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop worker: {str(e)}"
        )

@router.get("/worker/status")
async def get_worker_status():
    """
    Get replay worker status
    """
    return {
        "is_running": replay_worker.is_running,
        "queue_size": replay_worker.processing_queue.qsize(),
        "total_jobs": len(replay_worker.jobs)
    }
