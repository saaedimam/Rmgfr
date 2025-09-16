"""
Analytics API router for advanced fraud analytics
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from datetime import datetime, timedelta
import json

from ..models.database import get_db, Event, Decision, Profile
from ...advanced_analytics import analytics_engine
from ...real_time_dashboard import dashboard
from ...performance_monitor import performance_monitor

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_data(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time dashboard data"""
    try:
        # Get recent events and decisions
        events_result = await db.execute(
            select(Event).where(
                and_(
                    Event.project_id == project_id,
                    Event.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            ).order_by(desc(Event.created_at)).limit(1000)
        )
        events = events_result.scalars().all()
        
        decisions_result = await db.execute(
            select(Decision).where(
                and_(
                    Decision.project_id == project_id,
                    Decision.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            ).order_by(desc(Decision.created_at)).limit(1000)
        )
        decisions = decisions_result.scalars().all()
        
        # Convert to dict format
        events_data = [
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "risk_score": getattr(event, 'risk_score', 0),
                "timestamp": event.created_at.isoformat(),
                "user_id": event.profile_id,
                "device_fingerprint": event.device_fingerprint,
                "ip_address": getattr(event, 'ip_address', None),
                "location": getattr(event, 'location', None),
                "response_time_ms": getattr(event, 'response_time_ms', 0)
            }
            for event in events
        ]
        
        decisions_data = [
            {
                "id": str(decision.id),
                "outcome": decision.outcome,
                "risk_score": decision.risk_score,
                "timestamp": decision.created_at.isoformat(),
                "reason": decision.reason
            }
            for decision in decisions
        ]
        
        # Update dashboard metrics
        await dashboard.update_metrics(events_data, decisions_data)
        
        # Get dashboard data
        dashboard_data = await dashboard.get_dashboard_data()
        alerts = await dashboard.get_alerts()
        
        return {
            "dashboard": dashboard_data,
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

@router.get("/patterns")
async def get_fraud_patterns(
    project_id: str,
    hours: int = Query(24, description="Number of hours to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get detected fraud patterns"""
    try:
        # Get events from specified time period
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        events_result = await db.execute(
            select(Event).where(
                and_(
                    Event.project_id == project_id,
                    Event.created_at >= cutoff_time
                )
            ).order_by(desc(Event.created_at))
        )
        events = events_result.scalars().all()
        
        # Convert to dict format
        events_data = [
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "risk_score": getattr(event, 'risk_score', 0),
                "timestamp": event.created_at.isoformat(),
                "user_id": event.profile_id,
                "device_fingerprint": event.device_fingerprint,
                "ip_address": getattr(event, 'ip_address', None),
                "location": getattr(event, 'location', None)
            }
            for event in events
        ]
        
        # Analyze fraud patterns
        patterns = await analytics_engine.analyze_fraud_patterns(events_data)
        
        return {
            "patterns": [
                {
                    "pattern_id": pattern.pattern_id,
                    "name": pattern.name,
                    "description": pattern.description,
                    "risk_score": pattern.risk_score,
                    "frequency": pattern.frequency,
                    "last_seen": pattern.last_seen.isoformat(),
                    "affected_users": pattern.affected_users,
                    "false_positive_rate": pattern.false_positive_rate
                }
                for pattern in patterns
            ],
            "analysis_period_hours": hours,
            "total_events_analyzed": len(events_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze fraud patterns: {str(e)}"
        )

@router.get("/user-profiles")
async def get_user_profiles(
    project_id: str,
    user_id: Optional[str] = Query(None, description="Specific user ID to analyze"),
    limit: int = Query(100, description="Maximum number of profiles to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get user behavior profiles"""
    try:
        # Get events for analysis
        events_result = await db.execute(
            select(Event).where(
                and_(
                    Event.project_id == project_id,
                    Event.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).order_by(desc(Event.created_at)).limit(5000)
        )
        events = events_result.scalars().all()
        
        # Convert to dict format
        events_data = [
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "risk_score": getattr(event, 'risk_score', 0),
                "timestamp": event.created_at.isoformat(),
                "user_id": event.profile_id,
                "device_fingerprint": event.device_fingerprint,
                "location": getattr(event, 'location', None)
            }
            for event in events
        ]
        
        # Get unique user IDs
        if user_id:
            user_ids = [user_id]
        else:
            user_ids = list(set(e['user_id'] for e in events_data if e['user_id']))
        
        # Build profiles for each user
        profiles = []
        for uid in user_ids[:limit]:
            user_events = [e for e in events_data if e['user_id'] == uid]
            profile = await analytics_engine.build_user_profile(uid, user_events)
            profiles.append({
                "user_id": profile.user_id,
                "total_events": profile.total_events,
                "risk_score_avg": profile.risk_score_avg,
                "risk_score_trend": profile.risk_score_trend,
                "common_event_types": profile.common_event_types,
                "suspicious_activities": profile.suspicious_activities,
                "last_activity": profile.last_activity.isoformat(),
                "device_diversity": profile.device_diversity,
                "location_diversity": profile.location_diversity
            })
        
        return {
            "profiles": profiles,
            "total_profiles": len(profiles),
            "analysis_period_days": 30
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profiles: {str(e)}"
        )

@router.get("/insights")
async def get_risk_insights(
    project_id: str,
    hours: int = Query(24, description="Number of hours to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive risk insights"""
    try:
        # Get events from specified time period
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        events_result = await db.execute(
            select(Event).where(
                and_(
                    Event.project_id == project_id,
                    Event.created_at >= cutoff_time
                )
            ).order_by(desc(Event.created_at))
        )
        events = events_result.scalars().all()
        
        # Convert to dict format
        events_data = [
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "risk_score": getattr(event, 'risk_score', 0),
                "timestamp": event.created_at.isoformat(),
                "user_id": event.profile_id,
                "device_fingerprint": event.device_fingerprint,
                "ip_address": getattr(event, 'ip_address', None),
                "location": getattr(event, 'location', None)
            }
            for event in events
        ]
        
        # Generate insights
        insights = await analytics_engine.generate_risk_insights(events_data)
        
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate risk insights: {str(e)}"
        )

@router.get("/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        # Collect current metrics
        metrics = performance_monitor.collect_system_metrics()
        
        if not metrics:
            return {"message": "Unable to collect performance metrics"}
        
        # Get health status
        health_status = performance_monitor.get_health_status()
        
        # Get performance summary
        performance_summary = performance_monitor.get_performance_summary()
        
        return {
            "current_metrics": {
                "timestamp": metrics.timestamp.isoformat(),
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "memory_used_mb": metrics.memory_used_mb,
                "memory_available_mb": metrics.memory_available_mb,
                "disk_usage_percent": metrics.disk_usage_percent,
                "network_io_bytes": metrics.network_io_bytes,
                "active_connections": metrics.active_connections,
                "request_count": metrics.request_count,
                "error_count": metrics.error_count,
                "avg_response_time_ms": metrics.avg_response_time_ms,
                "p95_response_time_ms": metrics.p95_response_time_ms,
                "p99_response_time_ms": metrics.p99_response_time_ms
            },
            "health_status": health_status,
            "performance_summary": performance_summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )
