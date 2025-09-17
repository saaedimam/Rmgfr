"""
Tests for Replay Worker Service
"""

import pytest
import asyncio
from datetime import datetime
from src.services.replay_worker import ReplayWorker, ReplayStatus, ReplayJob

class TestReplayWorker:
    
    def setup_method(self):
        self.worker = ReplayWorker()
    
    @pytest.mark.asyncio
    async def test_enqueue_replay(self):
        """Test enqueueing a replay job"""
        event_ids = ["evt_1", "evt_2", "evt_3"]
        schema_version = 1
        reason = "rule_change:rule_42@v7"
        
        job_id = await self.worker.enqueue_replay(event_ids, schema_version, reason)
        
        assert job_id is not None
        assert job_id in self.worker.jobs
        
        job = self.worker.jobs[job_id]
        assert job.event_ids == event_ids
        assert job.schema_version == schema_version
        assert job.reason == reason
        assert job.status == ReplayStatus.PENDING
        assert job.total_count == len(event_ids)
    
    @pytest.mark.asyncio
    async def test_run_once_empty_queue(self):
        """Test run_once with empty queue"""
        result = await self.worker.run_once(limit=100)
        
        assert result["message"] == "No jobs in queue"
        assert result["processed"] == 0
    
    @pytest.mark.asyncio
    async def test_run_once_with_jobs(self):
        """Test run_once with jobs in queue"""
        # Enqueue a job
        event_ids = ["evt_1", "evt_2"]
        job_id = await self.worker.enqueue_replay(event_ids, 1, "test_reason")
        
        # Process the job
        result = await self.worker.run_once(limit=100)
        
        assert result["processed_jobs"] == 1
        assert result["processed_events"] == 2
        
        # Check job status
        job = self.worker.jobs[job_id]
        assert job.status == ReplayStatus.COMPLETED
        assert job.processed_count == 2
    
    @pytest.mark.asyncio
    async def test_get_job_status(self):
        """Test getting job status"""
        # Enqueue a job
        event_ids = ["evt_1"]
        job_id = await self.worker.enqueue_replay(event_ids, 1, "test_reason")
        
        # Get job status
        status = await self.worker.get_job_status(job_id)
        
        assert status is not None
        assert status["id"] == job_id
        assert status["status"] == ReplayStatus.PENDING.value
        assert status["total_count"] == 1
        assert status["processed_count"] == 0
    
    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self):
        """Test getting status of non-existent job"""
        status = await self.worker.get_job_status("non_existent_job")
        
        assert status is None
    
    @pytest.mark.asyncio
    async def test_list_jobs(self):
        """Test listing jobs"""
        # Enqueue multiple jobs
        job1 = await self.worker.enqueue_replay(["evt_1"], 1, "reason_1")
        job2 = await self.worker.enqueue_replay(["evt_2"], 2, "reason_2")
        
        # List all jobs
        jobs = await self.worker.list_jobs()
        
        assert len(jobs) == 2
        job_ids = [job["id"] for job in jobs]
        assert job1 in job_ids
        assert job2 in job_ids
    
    @pytest.mark.asyncio
    async def test_list_jobs_with_status_filter(self):
        """Test listing jobs with status filter"""
        # Enqueue a job and process it
        job_id = await self.worker.enqueue_replay(["evt_1"], 1, "test_reason")
        await self.worker.run_once(limit=100)
        
        # List completed jobs
        completed_jobs = await self.worker.list_jobs(status=ReplayStatus.COMPLETED)
        assert len(completed_jobs) == 1
        assert completed_jobs[0]["id"] == job_id
        
        # List pending jobs
        pending_jobs = await self.worker.list_jobs(status=ReplayStatus.PENDING)
        assert len(pending_jobs) == 0
    
    @pytest.mark.asyncio
    async def test_run_once_with_limit(self):
        """Test run_once with event limit"""
        # Enqueue a job with many events
        event_ids = [f"evt_{i}" for i in range(10)]
        job_id = await self.worker.enqueue_replay(event_ids, 1, "test_reason")
        
        # Process with limit
        result = await self.worker.run_once(limit=5)
        
        assert result["processed_events"] == 5
        assert result["processed_jobs"] == 1
        
        # Check job status
        job = self.worker.jobs[job_id]
        assert job.processed_count == 5
        assert job.status == ReplayStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_worker_lifecycle(self):
        """Test worker start/stop lifecycle"""
        # Start worker
        worker_task = asyncio.create_task(self.worker.start_worker())
        
        # Give it a moment to start
        await asyncio.sleep(0.1)
        
        # Check it's running
        assert self.worker.is_running
        
        # Stop worker
        await self.worker.stop_worker()
        
        # Give it a moment to stop
        await asyncio.sleep(0.1)
        
        # Check it's stopped
        assert not self.worker.is_running
        
        # Cancel the task
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in job processing"""
        # Create a job that will cause an error by mocking the process_event method
        original_process_event = self.worker._process_event
        
        async def mock_process_event(event_id, schema_version, reason):
            if event_id == "invalid_event":
                raise Exception("Simulated processing error")
            return await original_process_event(event_id, schema_version, reason)
        
        self.worker._process_event = mock_process_event
        
        try:
            job = ReplayJob(
                id="error_job",
                event_ids=["invalid_event"],
                schema_version=1,
                reason="test_error",
                status=ReplayStatus.PENDING,
                created_at=datetime.now(),
                total_count=1
            )
            
            self.worker.jobs["error_job"] = job
            await self.worker.processing_queue.put(job)
            
            # Process the job
            result = await self.worker.run_once(limit=100)
            
            # Check that error was handled
            assert result["processed_jobs"] == 1
            assert result["processed_events"] == 0
            
            # Check job status
            job = self.worker.jobs["error_job"]
            assert job.status == ReplayStatus.FAILED
            assert job.error_message is not None
            
        finally:
            # Restore original method
            self.worker._process_event = original_process_event

if __name__ == "__main__":
    pytest.main([__file__])
