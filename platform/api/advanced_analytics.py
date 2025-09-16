"""
Advanced Analytics Engine for Anti-Fraud Platform
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

@dataclass
class FraudPattern:
    pattern_id: str
    name: str
    description: str
    risk_score: float
    frequency: int
    last_seen: datetime
    affected_users: int
    false_positive_rate: float

@dataclass
class UserBehaviorProfile:
    user_id: str
    total_events: int
    risk_score_avg: float
    risk_score_trend: str  # "increasing", "decreasing", "stable"
    common_event_types: List[str]
    suspicious_activities: int
    last_activity: datetime
    device_diversity: int
    location_diversity: int

class AdvancedAnalytics:
    def __init__(self):
        self.fraud_patterns: Dict[str, FraudPattern] = {}
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.risk_trends: Dict[str, List[float]] = defaultdict(list)
    
    async def analyze_fraud_patterns(self, events: List[Dict[str, Any]]) -> List[FraudPattern]:
        """Analyze events to identify fraud patterns"""
        patterns = []
        
        # Pattern 1: Rapid successive events from same IP
        ip_events = defaultdict(list)
        for event in events:
            ip = event.get('ip_address', 'unknown')
            ip_events[ip].append(event)
        
        for ip, ip_event_list in ip_events.items():
            if len(ip_event_list) > 10:  # More than 10 events from same IP
                time_span = (max(e['timestamp'] for e in ip_event_list) - 
                           min(e['timestamp'] for e in ip_event_list)).total_seconds()
                if time_span < 300:  # Within 5 minutes
                    patterns.append(FraudPattern(
                        pattern_id=f"rapid_ip_{ip}",
                        name="Rapid IP Activity",
                        description=f"High frequency events from IP {ip}",
                        risk_score=0.8,
                        frequency=len(ip_event_list),
                        last_seen=datetime.utcnow(),
                        affected_users=len(set(e.get('user_id') for e in ip_event_list)),
                        false_positive_rate=0.1
                    ))
        
        # Pattern 2: Unusual time patterns
        hour_events = defaultdict(int)
        for event in events:
            hour = datetime.fromisoformat(event['timestamp']).hour
            hour_events[hour] += 1
        
        # Check for activity during unusual hours (2-6 AM)
        unusual_hour_activity = sum(hour_events.get(h, 0) for h in range(2, 6))
        if unusual_hour_activity > len(events) * 0.3:  # More than 30% during unusual hours
            patterns.append(FraudPattern(
                pattern_id="unusual_hours",
                name="Unusual Hour Activity",
                description="High activity during unusual hours (2-6 AM)",
                risk_score=0.6,
                frequency=unusual_hour_activity,
                last_seen=datetime.utcnow(),
                affected_users=len(set(e.get('user_id') for e in events)),
                false_positive_rate=0.2
            ))
        
        # Pattern 3: Device fingerprint clustering
        device_events = defaultdict(list)
        for event in events:
            device = event.get('device_fingerprint', 'unknown')
            device_events[device].append(event)
        
        for device, device_event_list in device_events.items():
            if len(device_event_list) > 5:
                users = set(e.get('user_id') for e in device_event_list)
                if len(users) > 3:  # Multiple users from same device
                    patterns.append(FraudPattern(
                        pattern_id=f"device_sharing_{device}",
                        name="Device Sharing",
                        description=f"Multiple users from same device {device}",
                        risk_score=0.7,
                        frequency=len(device_event_list),
                        last_seen=datetime.utcnow(),
                        affected_users=len(users),
                        false_positive_rate=0.15
                    ))
        
        return patterns
    
    async def build_user_profile(self, user_id: str, events: List[Dict[str, Any]]) -> UserBehaviorProfile:
        """Build comprehensive user behavior profile"""
        user_events = [e for e in events if e.get('user_id') == user_id]
        
        if not user_events:
            return UserBehaviorProfile(
                user_id=user_id,
                total_events=0,
                risk_score_avg=0,
                risk_score_trend="stable",
                common_event_types=[],
                suspicious_activities=0,
                last_activity=datetime.utcnow(),
                device_diversity=0,
                location_diversity=0
            )
        
        # Calculate risk score trend
        risk_scores = [e.get('risk_score', 0) for e in user_events]
        avg_risk_score = statistics.mean(risk_scores) if risk_scores else 0
        
        # Determine trend
        if len(risk_scores) >= 3:
            recent_avg = statistics.mean(risk_scores[-3:])
            older_avg = statistics.mean(risk_scores[:-3])
            if recent_avg > older_avg * 1.2:
                trend = "increasing"
            elif recent_avg < older_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Common event types
        event_types = [e.get('event_type', 'unknown') for e in user_events]
        common_types = [event_type for event_type, count in Counter(event_types).most_common(3)]
        
        # Suspicious activities (events with high risk scores)
        suspicious_count = sum(1 for score in risk_scores if score > 0.7)
        
        # Device and location diversity
        devices = set(e.get('device_fingerprint', 'unknown') for e in user_events)
        locations = set(e.get('location', 'unknown') for e in user_events)
        
        return UserBehaviorProfile(
            user_id=user_id,
            total_events=len(user_events),
            risk_score_avg=avg_risk_score,
            risk_score_trend=trend,
            common_event_types=common_types,
            suspicious_activities=suspicious_count,
            last_activity=max(datetime.fromisoformat(e['timestamp']) for e in user_events),
            device_diversity=len(devices),
            location_diversity=len(locations)
        )
    
    async def generate_risk_insights(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive risk insights"""
        if not events:
            return {"message": "No events to analyze"}
        
        # Overall statistics
        total_events = len(events)
        high_risk_events = [e for e in events if e.get('risk_score', 0) > 0.7]
        medium_risk_events = [e for e in events if 0.3 < e.get('risk_score', 0) <= 0.7]
        low_risk_events = [e for e in events if e.get('risk_score', 0) <= 0.3]
        
        # Risk distribution
        risk_distribution = {
            "high_risk": len(high_risk_events),
            "medium_risk": len(medium_risk_events),
            "low_risk": len(low_risk_events)
        }
        
        # Event type analysis
        event_types = [e.get('event_type', 'unknown') for e in events]
        event_type_counts = dict(Counter(event_types))
        
        # Time-based analysis
        hourly_distribution = defaultdict(int)
        for event in events:
            hour = datetime.fromisoformat(event['timestamp']).hour
            hourly_distribution[hour] += 1
        
        # Geographic analysis (if location data available)
        locations = [e.get('location', 'unknown') for e in events if e.get('location')]
        location_counts = dict(Counter(locations))
        
        # Device analysis
        devices = [e.get('device_fingerprint', 'unknown') for e in events if e.get('device_fingerprint')]
        device_counts = dict(Counter(devices))
        
        return {
            "summary": {
                "total_events": total_events,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "risk_distribution": risk_distribution,
                "high_risk_percentage": (len(high_risk_events) / total_events * 100) if total_events > 0 else 0
            },
            "event_types": event_type_counts,
            "hourly_distribution": dict(hourly_distribution),
            "top_locations": dict(Counter(locations).most_common(10)),
            "top_devices": dict(Counter(devices).most_common(10)),
            "recommendations": await self._generate_recommendations(events)
        }
    
    async def _generate_recommendations(self, events: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # High risk event recommendation
        high_risk_count = sum(1 for e in events if e.get('risk_score', 0) > 0.7)
        if high_risk_count > len(events) * 0.1:  # More than 10% high risk
            recommendations.append("Consider implementing stricter fraud detection rules - high risk events exceed 10%")
        
        # Time-based recommendation
        night_events = sum(1 for e in events 
                          if 2 <= datetime.fromisoformat(e['timestamp']).hour <= 6)
        if night_events > len(events) * 0.2:  # More than 20% during night
            recommendations.append("Review night-time activity patterns - consider additional verification for off-hours transactions")
        
        # Device diversity recommendation
        unique_devices = len(set(e.get('device_fingerprint', 'unknown') for e in events))
        if unique_devices < len(events) * 0.1:  # Less than 10% device diversity
            recommendations.append("Low device diversity detected - consider implementing device fingerprinting improvements")
        
        return recommendations

# Global analytics instance
analytics_engine = AdvancedAnalytics()
