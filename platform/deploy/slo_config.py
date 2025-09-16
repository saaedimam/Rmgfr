from dataclasses import dataclass
from typing import Dict, Any
import time
import asyncio
from datetime import datetime, timedelta

@dataclass
class SLOConfig:
    p99_9_latency_ms: int = 400
    error_rate_threshold: float = 0.001  # 0.1%
    error_budget_window_hours: int = 24
    max_errors_per_window: int = 100
    
    def check_latency_slo(self, latency_ms: float) -> bool:
        return latency_ms <= self.p99_9_latency_ms
    
    def check_error_rate_slo(self, errors: int, total_requests: int) -> bool:
        if total_requests == 0:
            return True
        error_rate = errors / total_requests
        return error_rate <= self.error_rate_threshold

class SLOMonitor:
    def __init__(self, config: SLOConfig):
        self.config = config
        self.metrics = {
            'requests': 0,
            'errors': 0,
            'latencies': []
        }
    
    async def record_request(self, latency_ms: float, is_error: bool = False):
        self.metrics['requests'] += 1
        if is_error:
            self.metrics['errors'] += 1
        self.metrics['latencies'].append(latency_ms)
        
        # Check SLO violations
        if not self.config.check_latency_slo(latency_ms):
            await self._handle_slo_violation('latency', latency_ms)
        
        if not self.config.check_error_rate_slo(self.metrics['errors'], self.metrics['requests']):
            await self._handle_slo_violation('error_rate', self.metrics['errors'] / self.metrics['requests'])
    
    async def _handle_slo_violation(self, violation_type: str, value: float):
        # In production, this would trigger rollback procedures
        print(f"🚨 SLO VIOLATION: {violation_type} = {value}")
        # TODO: Implement actual rollback logic
