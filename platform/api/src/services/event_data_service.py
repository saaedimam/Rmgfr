"""
Data access service for fraud detection
Separates data fetching from business logic
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
import logging

from ..models.database import Event, Profile, Rule
from .decision_core import EventContext, ProfileContext, RuleCondition

logger = logging.getLogger(__name__)

class EventDataService:
    """Service for fetching event-related data for fraud detection"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_event_context(self, event_id: str, project_id: str) -> Optional[EventContext]:
        """Get event context for decision making"""
        try:
            event_result = await self.db.execute(
                select(Event).where(
                    and_(
                        Event.id == event_id,
                        Event.project_id == project_id
                    )
                )
            )
            event = event_result.scalar_one_or_none()

            if not event:
                return None

            return EventContext(
                event_type=event.event_type,
                event_data=event.event_data or {},
                profile_id=str(event.profile_id) if event.profile_id else None,
                device_fingerprint=event.device_fingerprint,
                ip_address=event.ip_address,
                amount=event.amount,
                created_at=event.created_at.isoformat(),
                project_id=str(event.project_id)
            )
        except Exception as e:
            logger.error(f"Failed to get event context: {e}")
            return None

    async def get_profile_context(self, profile_id: str) -> Optional[ProfileContext]:
        """Get profile context for decision making"""
        try:
            profile_result = await self.db.execute(
                select(Profile).where(Profile.id == profile_id)
            )
            profile = profile_result.scalar_one_or_none()

            if not profile:
                return None

            return ProfileContext(
                id=str(profile.id),
                created_at=profile.created_at.isoformat(),
                last_activity=getattr(profile, 'last_activity', None)
            )
        except Exception as e:
            logger.error(f"Failed to get profile context: {e}")
            return None

    async def get_enabled_rules(self, project_id: str) -> List[Dict[str, Any]]:
        """Get enabled rules for project"""
        try:
            rules_result = await self.db.execute(
                select(Rule).where(
                    and_(
                        Rule.project_id == project_id,
                        Rule.enabled == True
                    )
                ).order_by(Rule.priority.desc())
            )
            rules = rules_result.scalars().all()

            return [
                {
                    "id": str(rule.id),
                    "name": rule.name,
                    "rule_type": rule.rule_type,
                    "conditions": rule.conditions or {},
                    "action": rule.action,
                    "priority": rule.priority
                }
                for rule in rules
            ]
        except Exception as e:
            logger.error(f"Failed to get enabled rules: {e}")
            return []

    async def get_event_count_for_rate_limit(
        self,
        project_id: str,
        scope: str,
        identifier: str,
        time_window_minutes: int,
        event_created_at: datetime
    ) -> int:
        """Get event count for rate limiting"""
        try:
            start_time = event_created_at - timedelta(minutes=time_window_minutes)

            if scope == "ip":
                count_query = select(func.count()).select_from(Event).where(
                    and_(
                        Event.project_id == project_id,
                        Event.ip_address == identifier,
                        Event.created_at >= start_time
                    )
                )
            elif scope == "profile":
                count_query = select(func.count()).select_from(Event).where(
                    and_(
                        Event.project_id == project_id,
                        Event.profile_id == identifier,
                        Event.created_at >= start_time
                    )
                )
            else:
                return 0

            count_result = await self.db.execute(count_query)
            return count_result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to get event count for rate limit: {e}")
            return 0

    async def get_event_count_for_velocity(
        self,
        project_id: str,
        profile_id: str,
        time_window_minutes: int,
        event_created_at: datetime
    ) -> int:
        """Get event count for velocity checking"""
        try:
            start_time = event_created_at - timedelta(minutes=time_window_minutes)

            count_query = select(func.count()).select_from(Event).where(
                and_(
                    Event.project_id == project_id,
                    Event.profile_id == profile_id,
                    Event.created_at >= start_time
                )
            )

            count_result = await self.db.execute(count_query)
            return count_result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to get event count for velocity: {e}")
            return 0

    async def get_device_usage_count(
        self,
        project_id: str,
        device_fingerprint: str,
        days: int = 30,
        event_created_at: datetime = None
    ) -> int:
        """Get device usage count for device fingerprinting"""
        try:
            if not event_created_at:
                event_created_at = datetime.utcnow()

            start_time = event_created_at - timedelta(days=days)

            count_query = select(func.count()).select_from(Event).where(
                and_(
                    Event.project_id == project_id,
                    Event.device_fingerprint == device_fingerprint,
                    Event.created_at >= start_time
                )
            )

            count_result = await self.db.execute(count_query)
            return count_result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to get device usage count: {e}")
            return 0
