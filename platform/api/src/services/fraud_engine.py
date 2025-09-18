"""
Fraud detection engine with rule evaluation
Refactored to use pure decision core and data service
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..models.database import Event, Profile, Rule, Decision
from .decision_core import DecisionCore, EventContext, ProfileContext
from .event_data_service import EventDataService

logger = logging.getLogger(__name__)

class FraudEngine:
    """Main fraud detection engine - orchestrates data and decision logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.decision_core = DecisionCore()
        self.data_service = EventDataService(db)

    async def evaluate_event(self, event_id: str, project_id: str) -> Dict[str, Any]:
        """Evaluate an event against all enabled rules"""
        try:
            # Get event context
            event_context = await self.data_service.get_event_context(event_id, project_id)
            if not event_context:
                raise ValueError("Event not found")

            # Get profile context if exists
            profile_context = None
            if event_context.profile_id:
                profile_context = await self.data_service.get_profile_context(event_context.profile_id)

            # Get enabled rules
            rules = await self.data_service.get_enabled_rules(project_id)

            # Evaluate rules using pure decision core
            rule_results = self.decision_core.evaluate_rules(rules, event_context, profile_context)

            # Make final decision
            decision_result = self.decision_core.make_decision(rule_results, event_context)

            return {
                "decision": decision_result.decision,
                "risk_score": decision_result.risk_score,
                "reasons": decision_result.reasons,
                "rules_fired": decision_result.rules_fired,
                "metadata": decision_result.metadata
            }

        except Exception as e:
            logger.error(f"Failed to evaluate event: {e}")
            raise Exception(f"Failed to evaluate event: {str(e)}")

    # Legacy method for backward compatibility
    async def calculate_risk_score(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        profile_id: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        ip_address: Optional[str] = None,
        amount: Optional[float] = None,
        session_id: Optional[str] = None
    ) -> float:
        """
        Calculate risk score using the new architecture
        This method maintains backward compatibility
        """
        try:
            # Create event context
            event_context = EventContext(
                event_type=event_type,
                event_data=event_data or {},
                profile_id=profile_id,
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                amount=amount,
                created_at=datetime.utcnow().isoformat(),
                project_id="default"  # This would come from the calling context
            )

            # Get profile context if exists
            profile_context = None
            if profile_id:
                profile_context = await self.data_service.get_profile_context(profile_id)

            # Get enabled rules (using default project for now)
            rules = await self.data_service.get_enabled_rules("default")

            # Evaluate rules using pure decision core
            rule_results = self.decision_core.evaluate_rules(rules, event_context, profile_context)

            # Make final decision
            decision_result = self.decision_core.make_decision(rule_results, event_context)

            return decision_result.risk_score

        except Exception as e:
            logger.error(f"Failed to calculate risk score: {e}")
            return 0.5  # Default risk score on error
