"""
Real-time Dashboard API router
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import logging

from ..services.database import get_database, DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])

class DashboardStats(BaseModel):
    total_events: int
    allowed_events: int
    denied_events: int
    review_events: int
    avg_risk_score: float
    max_risk_score: float
    min_risk_score: float
    time_period_hours: int
    last_updated: datetime

class EventTrend(BaseModel):
    timestamp: datetime
    total_events: int
    allowed_events: int
    denied_events: int
    review_events: int
    avg_risk_score: float

class TopRule(BaseModel):
    rule_name: str
    fire_count: int
    deny_count: int
    allow_count: int
    review_count: int

class DashboardResponse(BaseModel):
    stats: DashboardStats
    trends: List[EventTrend]
    top_rules: List[TopRule]
    recent_events: List[Dict[str, Any]]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    project_id: str,
    hours: int = Query(24, description="Time period in hours"),
    db: DatabaseService = Depends(get_database)
):
    """
    Get dashboard statistics for a project
    """
    try:
        # Get basic stats
        stats_sql = """
        SELECT
            COUNT(*) as total_events,
            COUNT(CASE WHEN decision = 'allow' THEN 1 END) as allowed_events,
            COUNT(CASE WHEN decision = 'deny' THEN 1 END) as denied_events,
            COUNT(CASE WHEN decision = 'review' THEN 1 END) as review_events,
            AVG(risk_score) as avg_risk_score,
            MAX(risk_score) as max_risk_score,
            MIN(risk_score) as min_risk_score
        FROM events
        WHERE project_id = $1
        AND created_at >= NOW() - INTERVAL '${hours} hours'
        """

        stats = await db.execute_one(stats_sql, project_id)

        if not stats:
            return DashboardStats(
                total_events=0,
                allowed_events=0,
                denied_events=0,
                review_events=0,
                avg_risk_score=0.0,
                max_risk_score=0.0,
                min_risk_score=0.0,
                time_period_hours=hours,
                last_updated=datetime.now()
            )

        return DashboardStats(
            total_events=stats["total_events"],
            allowed_events=stats["allowed_events"],
            denied_events=stats["denied_events"],
            review_events=stats["review_events"],
            avg_risk_score=float(stats["avg_risk_score"]) if stats["avg_risk_score"] else 0.0,
            max_risk_score=float(stats["max_risk_score"]) if stats["max_risk_score"] else 0.0,
            min_risk_score=float(stats["min_risk_score"]) if stats["min_risk_score"] else 0.0,
            time_period_hours=hours,
            last_updated=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@router.get("/trends", response_model=List[EventTrend])
async def get_event_trends(
    project_id: str,
    hours: int = Query(24, description="Time period in hours"),
    interval_minutes: int = Query(60, description="Interval in minutes"),
    db: DatabaseService = Depends(get_database)
):
    """
    Get event trends over time
    """
    try:
        # Calculate number of intervals
        num_intervals = (hours * 60) // interval_minutes

        trends_sql = """
        WITH time_series AS (
            SELECT
                generate_series(
                    NOW() - INTERVAL '${hours} hours',
                    NOW(),
                    INTERVAL '${interval_minutes} minutes'
                ) as time_bucket
        ),
        event_buckets AS (
            SELECT
                ts.time_bucket,
                COUNT(e.id) as total_events,
                COUNT(CASE WHEN e.decision = 'allow' THEN 1 END) as allowed_events,
                COUNT(CASE WHEN e.decision = 'deny' THEN 1 END) as denied_events,
                COUNT(CASE WHEN e.decision = 'review' THEN 1 END) as review_events,
                AVG(e.risk_score) as avg_risk_score
            FROM time_series ts
            LEFT JOIN events e ON
                e.project_id = $1
                AND e.created_at >= ts.time_bucket
                AND e.created_at < ts.time_bucket + INTERVAL '${interval_minutes} minutes'
            GROUP BY ts.time_bucket
            ORDER BY ts.time_bucket
        )
        SELECT
            time_bucket as timestamp,
            COALESCE(total_events, 0) as total_events,
            COALESCE(allowed_events, 0) as allowed_events,
            COALESCE(denied_events, 0) as denied_events,
            COALESCE(review_events, 0) as review_events,
            COALESCE(avg_risk_score, 0.0) as avg_risk_score
        FROM event_buckets
        """

        trends = await db.execute_query(trends_sql, project_id)

        return [
            EventTrend(
                timestamp=trend["timestamp"],
                total_events=trend["total_events"],
                allowed_events=trend["allowed_events"],
                denied_events=trend["denied_events"],
                review_events=trend["review_events"],
                avg_risk_score=float(trend["avg_risk_score"]) if trend["avg_risk_score"] else 0.0
            )
            for trend in trends
        ]

    except Exception as e:
        logger.error(f"Failed to get event trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event trends: {str(e)}"
        )

@router.get("/top-rules", response_model=List[TopRule])
async def get_top_rules(
    project_id: str,
    hours: int = Query(24, description="Time period in hours"),
    limit: int = Query(10, description="Number of rules to return"),
    db: DatabaseService = Depends(get_database)
):
    """
    Get top firing rules
    """
    try:
        # This would typically come from a rules_fired table
        # For now, we'll use simplified logic based on decisions
        rules_sql = """
        SELECT
            'risk_band_' || CASE
                WHEN risk_score < 0.3 THEN 'low'
                WHEN risk_score < 0.6 THEN 'medium'
                WHEN risk_score < 0.8 THEN 'high'
                ELSE 'critical'
            END as rule_name,
            COUNT(*) as fire_count,
            COUNT(CASE WHEN decision = 'deny' THEN 1 END) as deny_count,
            COUNT(CASE WHEN decision = 'allow' THEN 1 END) as allow_count,
            COUNT(CASE WHEN decision = 'review' THEN 1 END) as review_count
        FROM events
        WHERE project_id = $1
        AND created_at >= NOW() - INTERVAL '${hours} hours'
        GROUP BY rule_name
        ORDER BY fire_count DESC
        LIMIT $2
        """

        rules = await db.execute_query(rules_sql, project_id, limit)

        return [
            TopRule(
                rule_name=rule["rule_name"],
                fire_count=rule["fire_count"],
                deny_count=rule["deny_count"],
                allow_count=rule["allow_count"],
                review_count=rule["review_count"]
            )
            for rule in rules
        ]

    except Exception as e:
        logger.error(f"Failed to get top rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top rules: {str(e)}"
        )

@router.get("/recent-events", response_model=List[Dict[str, Any]])
async def get_recent_events(
    project_id: str,
    limit: int = Query(50, description="Number of events to return"),
    db: DatabaseService = Depends(get_database)
):
    """
    Get recent events for the dashboard
    """
    try:
        events_sql = """
        SELECT
            e.id,
            e.event_type,
            e.profile_id,
            e.ip_address,
            e.risk_score,
            e.decision,
            e.created_at,
            d.reasons,
            d.rules_fired
        FROM events e
        LEFT JOIN decisions d ON e.id = d.event_id
        WHERE e.project_id = $1
        ORDER BY e.created_at DESC
        LIMIT $2
        """

        events = await db.execute_query(events_sql, project_id, limit)

        return [
            {
                "id": event["id"],
                "event_type": event["event_type"],
                "profile_id": event["profile_id"],
                "ip_address": event["ip_address"],
                "risk_score": float(event["risk_score"]) if event["risk_score"] else 0.0,
                "decision": event["decision"],
                "reasons": event["reasons"] or [],
                "rules_fired": event["rules_fired"] or [],
                "created_at": event["created_at"].isoformat()
            }
            for event in events
        ]

    except Exception as e:
        logger.error(f"Failed to get recent events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent events: {str(e)}"
        )

@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    project_id: str,
    hours: int = Query(24, description="Time period in hours"),
    db: DatabaseService = Depends(get_database)
):
    """
    Get complete dashboard data
    """
    try:
        # Get all dashboard data in parallel
        stats_task = get_dashboard_stats(project_id, hours, db)
        trends_task = get_event_trends(project_id, hours, 60, db)
        rules_task = get_top_rules(project_id, hours, 10, db)
        events_task = get_recent_events(project_id, 50, db)

        # Wait for all tasks to complete
        stats, trends, rules, events = await asyncio.gather(
            stats_task, trends_task, rules_task, events_task
        )

        return DashboardResponse(
            stats=stats,
            trends=trends,
            top_rules=rules,
            recent_events=events
        )

    except Exception as e:
        logger.error(f"Failed to get dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard: {str(e)}"
        )
