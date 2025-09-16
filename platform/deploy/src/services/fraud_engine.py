"""
Fraud detection engine with rule evaluation
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import asyncio
import hashlib
import json

from ..models.database import Event, Profile, Rule, Decision

class FraudEngine:
    """Main fraud detection engine"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def evaluate_event(self, event_id: str, project_id: str) -> Dict[str, Any]:
        """Evaluate an event against all enabled rules"""
        try:
            # Get event
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
                raise ValueError("Event not found")
            
            # Get profile if exists
            profile = None
            if event.profile_id:
                profile_result = await self.db.execute(
                    select(Profile).where(Profile.id == event.profile_id)
                )
                profile = profile_result.scalar_one_or_none()
            
            # Get enabled rules for project
            rules_result = await self.db.execute(
                select(Rule).where(
                    and_(
                        Rule.project_id == project_id,
                        Rule.enabled == True
                    )
                ).order_by(Rule.priority.desc())
            )
            rules = rules_result.scalars().all()
            
            # Evaluate rules
            decision = "allow"
            risk_score = 0.0
            reasons = []
            rules_fired = []
            
            for rule in rules:
                rule_result = await self._evaluate_rule(rule, event, profile)
                if rule_result["fired"]:
                    rules_fired.append(rule.name)
                    reasons.append(rule_result["reason"])
                    
                    # Update decision based on rule action
                    if rule.action == "deny":
                        decision = "deny"
                        risk_score = max(risk_score, rule_result.get("risk_score", 0.8))
                    elif rule.action == "review" and decision == "allow":
                        decision = "review"
                        risk_score = max(risk_score, rule_result.get("risk_score", 0.6))
                    else:
                        risk_score = max(risk_score, rule_result.get("risk_score", 0.2))
            
            return {
                "decision": decision,
                "risk_score": risk_score,
                "reasons": reasons,
                "rules_fired": rules_fired,
                "metadata": {
                    "evaluated_at": datetime.utcnow().isoformat(),
                    "event_type": event.event_type,
                    "profile_id": str(event.profile_id) if event.profile_id else None
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to evaluate event: {str(e)}")
    
    async def _evaluate_rule(self, rule: Rule, event: Event, profile: Optional[Profile]) -> Dict[str, Any]:
        """Evaluate a single rule against event and profile"""
        try:
            if rule.rule_type == "rate_limit":
                return await self._evaluate_rate_limit_rule(rule, event, profile)
            elif rule.rule_type == "velocity":
                return await self._evaluate_velocity_rule(rule, event, profile)
            elif rule.rule_type == "device":
                return await self._evaluate_device_rule(rule, event, profile)
            elif rule.rule_type == "custom":
                return await self._evaluate_custom_rule(rule, event, profile)
            else:
                return {"fired": False, "reason": f"Unknown rule type: {rule.rule_type}"}
                
        except Exception as e:
            return {"fired": False, "reason": f"Rule evaluation error: {str(e)}"}
    
    async def _evaluate_rate_limit_rule(self, rule: Rule, event: Event, profile: Optional[Profile]) -> Dict[str, Any]:
        """Evaluate rate limiting rule"""
        conditions = rule.conditions
        time_window = conditions.get("time_window_minutes", 60)
        max_events = conditions.get("max_events", 100)
        
        # Calculate time window
        start_time = event.created_at - timedelta(minutes=time_window)
        
        # Count events in time window
        if conditions.get("scope") == "ip":
            count_query = select(func.count()).select_from(Event).where(
                and_(
                    Event.project_id == event.project_id,
                    Event.ip_address == event.ip_address,
                    Event.created_at >= start_time
                )
            )
        elif conditions.get("scope") == "profile" and profile:
            count_query = select(func.count()).select_from(Event).where(
                and_(
                    Event.project_id == event.project_id,
                    Event.profile_id == profile.id,
                    Event.created_at >= start_time
                )
            )
        else:
            return {"fired": False, "reason": "Invalid rate limit scope"}
        
        count_result = await self.db.execute(count_query)
        event_count = count_result.scalar()
        
        if event_count > max_events:
            return {
                "fired": True,
                "reason": f"Rate limit exceeded: {event_count} events in {time_window} minutes",
                "risk_score": min(0.9, event_count / max_events)
            }
        
        return {"fired": False, "reason": f"Rate limit OK: {event_count}/{max_events} events"}
    
    async def _evaluate_velocity_rule(self, rule: Rule, event: Event, profile: Optional[Profile]) -> Dict[str, Any]:
        """Evaluate velocity rule (events per time period)"""
        conditions = rule.conditions
        time_window = conditions.get("time_window_minutes", 60)
        max_velocity = conditions.get("max_velocity", 10)
        
        # Calculate time window
        start_time = event.created_at - timedelta(minutes=time_window)
        
        # Count events in time window
        if conditions.get("scope") == "profile" and profile:
            count_query = select(func.count()).select_from(Event).where(
                and_(
                    Event.project_id == event.project_id,
                    Event.profile_id == profile.id,
                    Event.created_at >= start_time
                )
            )
        else:
            return {"fired": False, "reason": "Invalid velocity scope"}
        
        count_result = await self.db.execute(count_query)
        event_count = count_result.scalar()
        
        if event_count > max_velocity:
            return {
                "fired": True,
                "reason": f"Velocity exceeded: {event_count} events in {time_window} minutes",
                "risk_score": min(0.8, event_count / max_velocity)
            }
        
        return {"fired": False, "reason": f"Velocity OK: {event_count}/{max_velocity} events"}
    
    async def _evaluate_device_rule(self, rule: Rule, event: Event, profile: Optional[Profile]) -> Dict[str, Any]:
        """Evaluate device fingerprinting rule"""
        conditions = rule.conditions
        
        if not event.device_fingerprint:
            return {"fired": False, "reason": "No device fingerprint available"}
        
        # Check for device reuse patterns
        if conditions.get("check_device_reuse"):
            device_query = select(func.count()).select_from(Event).where(
                and_(
                    Event.project_id == event.project_id,
                    Event.device_fingerprint == event.device_fingerprint,
                    Event.created_at >= event.created_at - timedelta(days=30)
                )
            )
            device_result = await self.db.execute(device_query)
            device_count = device_result.scalar()
            
            if device_count > conditions.get("max_device_uses", 5):
                return {
                    "fired": True,
                    "reason": f"Device overuse: {device_count} events from same device",
                    "risk_score": min(0.7, device_count / 10)
                }
        
        return {"fired": False, "reason": "Device fingerprint OK"}
    
    async def _evaluate_custom_rule(self, rule: Rule, event: Event, profile: Optional[Profile]) -> Dict[str, Any]:
        """Evaluate custom rule based on conditions"""
        conditions = rule.conditions
        
        # Example custom rule: check event data patterns
        if conditions.get("check_event_data"):
            event_data = event.event_data or {}
            
            # Check for suspicious patterns
            if conditions.get("suspicious_keywords"):
                keywords = conditions["suspicious_keywords"]
                for key, value in event_data.items():
                    if isinstance(value, str):
                        for keyword in keywords:
                            if keyword.lower() in value.lower():
                                return {
                                    "fired": True,
                                    "reason": f"Suspicious keyword detected: {keyword}",
                                    "risk_score": 0.6
                                }
        
        return {"fired": False, "reason": "Custom rule conditions not met"}
