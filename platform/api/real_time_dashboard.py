"""
Real-time Dashboard Data Provider for Anti-Fraud Platform
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics

@dataclass
class DashboardMetrics:
    timestamp: datetime
    total_events: int
    high_risk_events: int
    medium_risk_events: int
    low_risk_events: int
    blocked_transactions: int
    allowed_transactions: int
    pending_review: int
    avg_risk_score: float
    fraud_detection_rate: float
    false_positive_rate: float
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    active_users: int
    unique_devices: int
    top_event_types: List[Dict[str, Any]]
    top_risk_factors: List[Dict[str, Any]]
    geographic_distribution: List[Dict[str, Any]]
    hourly_trends: List[Dict[str, Any]]

class RealTimeDashboard:
    def __init__(self):
        self.metrics_history: List[DashboardMetrics] = []
        self.event_cache: List[Dict[str, Any]] = []
        self.user_sessions: Dict[str, datetime] = {}
        self.device_cache: set = set()
    
    async def update_metrics(self, events: List[Dict[str, Any]], decisions: List[Dict[str, Any]]):
        """Update dashboard metrics with latest data"""
        now = datetime.utcnow()
        
        # Filter events from last 24 hours
        cutoff_time = now - timedelta(hours=24)
        recent_events = [
            e for e in events 
            if datetime.fromisoformat(e.get('timestamp', now.isoformat())) >= cutoff_time
        ]
        
        # Calculate risk distribution
        high_risk = [e for e in recent_events if e.get('risk_score', 0) > 0.7]
        medium_risk = [e for e in recent_events if 0.3 < e.get('risk_score', 0) <= 0.7]
        low_risk = [e for e in recent_events if e.get('risk_score', 0) <= 0.3]
        
        # Calculate decision distribution
        blocked = [d for d in decisions if d.get('outcome') == 'deny']
        allowed = [d for d in decisions if d.get('outcome') == 'allow']
        pending = [d for d in decisions if d.get('outcome') == 'review']
        
        # Calculate average risk score
        risk_scores = [e.get('risk_score', 0) for e in recent_events]
        avg_risk_score = statistics.mean(risk_scores) if risk_scores else 0
        
        # Calculate fraud detection rate
        total_decisions = len(decisions)
        fraud_detection_rate = (len(blocked) / total_decisions * 100) if total_decisions > 0 else 0
        
        # Calculate false positive rate (simplified)
        false_positive_rate = 5.0  # Placeholder - would need manual review data
        
        # Calculate response times (simplified)
        response_times = [e.get('response_time_ms', 0) for e in recent_events if e.get('response_time_ms')]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else avg_response_time
        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else avg_response_time
        
        # Active users (last hour)
        hour_cutoff = now - timedelta(hours=1)
        recent_user_events = [
            e for e in recent_events 
            if datetime.fromisoformat(e.get('timestamp', now.isoformat())) >= hour_cutoff
        ]
        active_users = len(set(e.get('user_id') for e in recent_user_events if e.get('user_id')))
        
        # Unique devices
        unique_devices = len(set(e.get('device_fingerprint') for e in recent_events if e.get('device_fingerprint')))
        
        # Top event types
        event_types = [e.get('event_type', 'unknown') for e in recent_events]
        top_event_types = [
            {"type": event_type, "count": count, "percentage": count / len(recent_events) * 100}
            for event_type, count in Counter(event_types).most_common(5)
        ]
        
        # Top risk factors (simplified)
        top_risk_factors = [
            {"factor": "High velocity", "count": len([e for e in high_risk if 'velocity' in str(e)]), "impact": "High"},
            {"factor": "Suspicious location", "count": len([e for e in high_risk if 'location' in str(e)]), "impact": "Medium"},
            {"factor": "Device anomaly", "count": len([e for e in high_risk if 'device' in str(e)]), "impact": "High"},
            {"factor": "Time anomaly", "count": len([e for e in high_risk if 'time' in str(e)]), "impact": "Low"}
        ]
        
        # Geographic distribution (simplified)
        locations = [e.get('location', 'Unknown') for e in recent_events if e.get('location')]
        geographic_distribution = [
            {"location": location, "count": count, "risk_level": "High" if count > 10 else "Medium" if count > 5 else "Low"}
            for location, count in Counter(locations).most_common(10)
        ]
        
        # Hourly trends (last 24 hours)
        hourly_trends = []
        for hour in range(24):
            hour_events = [
                e for e in recent_events 
                if datetime.fromisoformat(e.get('timestamp', now.isoformat())).hour == hour
            ]
            hourly_trends.append({
                "hour": hour,
                "events": len(hour_events),
                "high_risk": len([e for e in hour_events if e.get('risk_score', 0) > 0.7]),
                "avg_risk_score": statistics.mean([e.get('risk_score', 0) for e in hour_events]) if hour_events else 0
            })
        
        # Create metrics object
        metrics = DashboardMetrics(
            timestamp=now,
            total_events=len(recent_events),
            high_risk_events=len(high_risk),
            medium_risk_events=len(medium_risk),
            low_risk_events=len(low_risk),
            blocked_transactions=len(blocked),
            allowed_transactions=len(allowed),
            pending_review=len(pending),
            avg_risk_score=avg_risk_score,
            fraud_detection_rate=fraud_detection_rate,
            false_positive_rate=false_positive_rate,
            response_time_avg=avg_response_time,
            response_time_p95=p95_response_time,
            response_time_p99=p99_response_time,
            active_users=active_users,
            unique_devices=unique_devices,
            top_event_types=top_event_types,
            top_risk_factors=top_risk_factors,
            geographic_distribution=geographic_distribution,
            hourly_trends=hourly_trends
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics for performance
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return metrics
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        if not self.metrics_history:
            return {"message": "No metrics available"}
        
        latest = self.metrics_history[-1]
        
        # Convert to dict for JSON serialization
        dashboard_data = asdict(latest)
        
        # Add trend data
        if len(self.metrics_history) >= 2:
            previous = self.metrics_history[-2]
            dashboard_data["trends"] = {
                "events_change": latest.total_events - previous.total_events,
                "risk_score_change": latest.avg_risk_score - previous.avg_risk_score,
                "fraud_rate_change": latest.fraud_detection_rate - previous.fraud_detection_rate,
                "response_time_change": latest.response_time_avg - previous.response_time_avg
            }
        
        return dashboard_data
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts based on metrics"""
        alerts = []
        
        if not self.metrics_history:
            return alerts
        
        latest = self.metrics_history[-1]
        
        # High risk events alert
        if latest.high_risk_events > latest.total_events * 0.2:  # More than 20% high risk
            alerts.append({
                "type": "warning",
                "title": "High Risk Events Spike",
                "message": f"High risk events ({latest.high_risk_events}) exceed 20% of total events",
                "timestamp": latest.timestamp.isoformat(),
                "severity": "high"
            })
        
        # Response time alert
        if latest.response_time_p99 > 1000:  # P99 > 1 second
            alerts.append({
                "type": "performance",
                "title": "High Response Time",
                "message": f"P99 response time ({latest.response_time_p99:.1f}ms) exceeds threshold",
                "timestamp": latest.timestamp.isoformat(),
                "severity": "medium"
            })
        
        # Fraud detection rate alert
        if latest.fraud_detection_rate > 50:  # More than 50% blocked
            alerts.append({
                "type": "fraud",
                "title": "High Fraud Detection Rate",
                "message": f"Fraud detection rate ({latest.fraud_detection_rate:.1f}%) is unusually high",
                "timestamp": latest.timestamp.isoformat(),
                "severity": "high"
            })
        
        return alerts

# Global dashboard instance
dashboard = RealTimeDashboard()
