"""
Advanced Performance Monitoring for Anti-Fraud Platform
"""

import time
import asyncio
import psutil
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io_bytes: int
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.request_times: List[float] = []
        self.error_count = 0
        self.request_count = 0
        self.start_time = time.time()
    
    def record_request(self, response_time_ms: float, is_error: bool = False):
        """Record a request and its performance metrics"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        
        self.request_times.append(response_time_ms)
        
        # Keep only last 1000 request times for performance
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Calculate response time percentiles
            if self.request_times:
                sorted_times = sorted(self.request_times)
                n = len(sorted_times)
                avg_response_time = sum(sorted_times) / n
                p95_index = int(n * 0.95)
                p99_index = int(n * 0.99)
                p95_response_time = sorted_times[p95_index] if p95_index < n else 0
                p99_response_time = sorted_times[p99_index] if p99_index < n else 0
            else:
                avg_response_time = 0
                p95_response_time = 0
                p99_response_time = 0
            
            return PerformanceMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io_bytes=network.bytes_sent + network.bytes_recv,
                active_connections=len(psutil.net_connections()),
                request_count=self.request_count,
                error_count=self.error_count,
                avg_response_time_ms=avg_response_time,
                p95_response_time_ms=p95_response_time,
                p99_response_time_ms=p99_response_time
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status based on metrics"""
        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics available"}
        
        latest = self.metrics_history[-1]
        
        # Health checks
        issues = []
        
        if latest.cpu_percent > 80:
            issues.append(f"High CPU usage: {latest.cpu_percent:.1f}%")
        
        if latest.memory_percent > 85:
            issues.append(f"High memory usage: {latest.memory_percent:.1f}%")
        
        if latest.disk_usage_percent > 90:
            issues.append(f"High disk usage: {latest.disk_usage_percent:.1f}%")
        
        if latest.p99_response_time_ms > 1000:
            issues.append(f"High P99 response time: {latest.p99_response_time_ms:.1f}ms")
        
        error_rate = (latest.error_count / latest.request_count * 100) if latest.request_count > 0 else 0
        if error_rate > 5:
            issues.append(f"High error rate: {error_rate:.1f}%")
        
        if issues:
            return {
                "status": "unhealthy",
                "message": "; ".join(issues),
                "issues": issues
            }
        else:
            return {
                "status": "healthy",
                "message": "All systems operational",
                "uptime_seconds": time.time() - self.start_time
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for the last hour"""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= one_hour_ago
        ]
        
        if not recent_metrics:
            return {"message": "No recent metrics available"}
        
        return {
            "period": "last_hour",
            "total_requests": recent_metrics[-1].request_count,
            "total_errors": recent_metrics[-1].error_count,
            "avg_cpu_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "avg_memory_percent": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            "avg_response_time_ms": recent_metrics[-1].avg_response_time_ms,
            "p95_response_time_ms": recent_metrics[-1].p95_response_time_ms,
            "p99_response_time_ms": recent_metrics[-1].p99_response_time_ms,
            "error_rate_percent": (recent_metrics[-1].error_count / recent_metrics[-1].request_count * 100) if recent_metrics[-1].request_count > 0 else 0
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
