"""
Replay Worker Service
Handles event replay for rule changes and data reprocessing
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ReplayStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ReplayJob:
    id: str
    event_ids: List[str]
    schema_version: int
    reason: str
    status: ReplayStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processed_count: int = 0
    total_count: int = 0

class ReplayWorker:
    """
    Replay worker for processing event replays
    """
    
    def __init__(self, db_pool=None):
        self.db_pool = db_pool
        self.jobs: Dict[str, ReplayJob] = {}
        self.is_running = False
        self.processing_queue = asyncio.Queue()
    
    async def enqueue_replay(
        self, 
        event_ids: List[str], 
        schema_version: int, 
        reason: str
    ) -> str:
        """
        Enqueue a new replay job
        
        Args:
            event_ids: List of event IDs to replay
            schema_version: Schema version for replay
            reason: Reason for replay (e.g., "rule_change:rule_42@v7")
            
        Returns:
            Job ID
        """
        job_id = f"replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.jobs)}"
        
        job = ReplayJob(
            id=job_id,
            event_ids=event_ids,
            schema_version=schema_version,
            reason=reason,
            status=ReplayStatus.PENDING,
            created_at=datetime.now(),
            total_count=len(event_ids)
        )
        
        self.jobs[job_id] = job
        await self.processing_queue.put(job)
        
        logger.info(f"Enqueued replay job {job_id} with {len(event_ids)} events")
        return job_id
    
    async def run_once(self, limit: int = 100) -> Dict[str, Any]:
        """
        Process one batch of replay jobs
        
        Args:
            limit: Maximum number of events to process
            
        Returns:
            Processing summary
        """
        if self.processing_queue.empty():
            return {"message": "No jobs in queue", "processed": 0}
        
        processed_jobs = 0
        processed_events = 0
        
        try:
            # Process up to limit events
            while processed_events < limit and not self.processing_queue.empty():
                job = await self.processing_queue.get()
                
                if job.status != ReplayStatus.PENDING:
                    continue
                
                # Update job status
                job.status = ReplayStatus.PROCESSING
                job.started_at = datetime.now()
                
                try:
                    # Process events in this job
                    events_processed = await self._process_job(job, limit - processed_events)
                    processed_events += events_processed
                    job.processed_count = events_processed
                    
                    # Mark job as completed
                    job.status = ReplayStatus.COMPLETED
                    job.completed_at = datetime.now()
                    
                    logger.info(f"Completed job {job.id}: {events_processed} events processed")
                    
                except Exception as e:
                    job.status = ReplayStatus.FAILED
                    job.error_message = str(e)
                    job.completed_at = datetime.now()
                    logger.error(f"Failed job {job.id}: {e}")
                
                processed_jobs += 1
                
        except Exception as e:
            logger.error(f"Error in run_once: {e}")
            return {"error": str(e), "processed": processed_events}
        
        return {
            "message": f"Processed {processed_jobs} jobs, {processed_events} events",
            "processed_jobs": processed_jobs,
            "processed_events": processed_events
        }
    
    async def _process_job(self, job: ReplayJob, max_events: int) -> int:
        """
        Process a single replay job
        
        Args:
            job: Replay job to process
            max_events: Maximum events to process in this batch
            
        Returns:
            Number of events processed
        """
        events_to_process = job.event_ids[:max_events]
        processed_count = 0
        failed_events = 0
        
        for event_id in events_to_process:
            try:
                # Simulate event processing
                await self._process_event(event_id, job.schema_version, job.reason)
                processed_count += 1
                
                # Simulate processing delay
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Failed to process event {event_id}: {e}")
                failed_events += 1
                # Continue with next event
        
        # If any events failed, mark the job as failed
        if failed_events > 0:
            job.status = ReplayStatus.FAILED
            job.error_message = f"Failed to process {failed_events} out of {len(events_to_process)} events"
            raise Exception(job.error_message)
        
        return processed_count
    
    async def _process_event(self, event_id: str, schema_version: int, reason: str):
        """
        Process a single event for replay
        
        Args:
            event_id: Event ID to process
            schema_version: Schema version for processing
            reason: Reason for replay
        """
        # This would typically:
        # 1. Fetch event from database
        # 2. Apply new rules/schema
        # 3. Recalculate risk score
        # 4. Update decision if needed
        # 5. Log the replay action
        
        logger.debug(f"Processing event {event_id} with schema v{schema_version} for reason: {reason}")
        
        # Simulate database operations
        await asyncio.sleep(0.001)
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a replay job
        
        Args:
            job_id: Job ID to check
            
        Returns:
            Job status information
        """
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "processed_count": job.processed_count,
            "total_count": job.total_count,
            "error_message": job.error_message
        }
    
    async def list_jobs(self, status: Optional[ReplayStatus] = None) -> List[Dict[str, Any]]:
        """
        List all replay jobs
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            List of job information
        """
        jobs = []
        for job in self.jobs.values():
            if status and job.status != status:
                continue
            
            jobs.append({
                "id": job.id,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "processed_count": job.processed_count,
                "total_count": job.total_count,
                "reason": job.reason
            })
        
        return sorted(jobs, key=lambda x: x["created_at"], reverse=True)
    
    async def start_worker(self):
        """Start the replay worker"""
        if self.is_running:
            logger.warning("Replay worker is already running")
            return
        
        self.is_running = True
        logger.info("Starting replay worker")
        
        try:
            while self.is_running:
                # Process jobs continuously
                result = await self.run_once(limit=10)
                logger.debug(f"Worker cycle: {result}")
                
                # Wait before next cycle
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in replay worker: {e}")
        finally:
            self.is_running = False
            logger.info("Replay worker stopped")
    
    async def stop_worker(self):
        """Stop the replay worker"""
        self.is_running = False
        logger.info("Stopping replay worker")

# Global instance
replay_worker = ReplayWorker()
