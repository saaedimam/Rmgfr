"""
Pure decision logic for fraud detection
Extracted from FraudEngine to separate business logic from data access
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RuleType(Enum):
    RATE_LIMIT = "rate_limit"
    VELOCITY = "velocity"
    DEVICE = "device"
    CUSTOM = "custom"

class RuleAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"

@dataclass
class RuleCondition:
    """Represents a rule condition for evaluation"""
    rule_type: RuleType
    scope: str  # 'ip', 'profile', 'device'
    time_window_minutes: int
    max_events: int
    max_velocity: int
    max_device_uses: int
    suspicious_keywords: List[str]
    check_device_reuse: bool
    check_event_data: bool

@dataclass
class EventContext:
    """Pure event context for decision making"""
    event_type: str
    event_data: Dict[str, Any]
    profile_id: Optional[str]
    device_fingerprint: Optional[str]
    ip_address: Optional[str]
    amount: Optional[float]
    created_at: str
    project_id: str

@dataclass
class ProfileContext:
    """Profile context for decision making"""
    id: str
    created_at: str
    last_activity: Optional[str]

@dataclass
class RuleResult:
    """Result of rule evaluation"""
    fired: bool
    reason: str
    risk_score: float
    rule_name: str

@dataclass
class DecisionResult:
    """Final decision result"""
    decision: str
    risk_score: float
    reasons: List[str]
    rules_fired: List[str]
    metadata: Dict[str, Any]

class DecisionCore:
    """
    Pure decision logic for fraud detection
    Now uses table-driven rule engine and decision matrix
    """

    def __init__(self):
        self.risk_weights = {
            'velocity': 0.3,
            'device_anomaly': 0.25,
            'geolocation': 0.2,
            'behavioral': 0.15,
            'payment_risk': 0.1
        }

        # Initialize table-driven components
        from .rule_engine import TableDrivenRuleEngine
        from .decision_matrix import DecisionMatrixFactory

        self.rule_engine = TableDrivenRuleEngine()
        self.decision_matrix = DecisionMatrixEngine(
            DecisionMatrixFactory.create_default_config()
        )

    def evaluate_rules(
        self,
        rules: List[Dict[str, Any]],
        event: EventContext,
        profile: Optional[ProfileContext] = None
    ) -> List[RuleResult]:
        """
        Evaluate all rules using table-driven rule engine

        Args:
            rules: List of rule definitions
            event: Event context
            profile: Optional profile context

        Returns:
            List of rule evaluation results
        """
        # Convert rule definitions to RuleDefinition objects
        rule_definitions = []
        for rule in rules:
            try:
                rule_def = RuleDefinition(
                    name=rule.get('name', 'unnamed'),
                    rule_type=RuleType(rule.get('rule_type', 'custom')),
                    conditions=rule.get('conditions', {}),
                    action=RuleAction(rule.get('action', 'review')),
                    priority=rule.get('priority', 0),
                    enabled=rule.get('enabled', True),
                    description=rule.get('description', '')
                )
                rule_definitions.append(rule_def)
            except Exception as e:
                logger.warning(f"Failed to create rule definition for {rule.get('name', 'unknown')}: {e}")
                continue

        # Create evaluation context with pre-calculated data
        evaluation_context = RuleEvaluationContext(
            event=event,
            profile=profile,
            event_counts={},  # This would be populated by the data service
            device_usage_count=0,  # This would be populated by the data service
            ip_geolocation=None,  # This would be populated by the data service
            user_behavior_score=0.0  # This would be calculated
        )

        # Use table-driven rule engine
        return self.rule_engine.evaluate_rules(rule_definitions, evaluation_context)

    def _evaluate_single_rule(
        self,
        rule: Dict[str, Any],
        event: EventContext,
        profile: Optional[ProfileContext]
    ) -> RuleResult:
        """Evaluate a single rule"""
        rule_type = RuleType(rule.get('rule_type', 'custom'))
        conditions = rule.get('conditions', {})
        rule_name = rule.get('name', 'unnamed')

        if rule_type == RuleType.RATE_LIMIT:
            return self._evaluate_rate_limit_rule(rule_name, conditions, event, profile)
        elif rule_type == RuleType.VELOCITY:
            return self._evaluate_velocity_rule(rule_name, conditions, event, profile)
        elif rule_type == RuleType.DEVICE:
            return self._evaluate_device_rule(rule_name, conditions, event, profile)
        elif rule_type == RuleType.CUSTOM:
            return self._evaluate_custom_rule(rule_name, conditions, event, profile)
        else:
            return RuleResult(
                fired=False,
                reason=f"Unknown rule type: {rule_type}",
                risk_score=0.0,
                rule_name=rule_name
            )

    def _evaluate_rate_limit_rule(
        self,
        rule_name: str,
        conditions: Dict[str, Any],
        event: EventContext,
        profile: Optional[ProfileContext]
    ) -> RuleResult:
        """Evaluate rate limiting rule (pure logic)"""
        time_window = conditions.get("time_window_minutes", 60)
        max_events = conditions.get("max_events", 100)
        scope = conditions.get("scope", "ip")

        # This would be called with actual event counts from the data layer
        # For now, we return a placeholder that indicates this needs data
        if scope == "ip" and not event.ip_address:
            return RuleResult(
                fired=False,
                reason="No IP address for rate limiting",
                risk_score=0.0,
                rule_name=rule_name
            )

        if scope == "profile" and not profile:
            return RuleResult(
                fired=False,
                reason="No profile for rate limiting",
                risk_score=0.0,
                rule_name=rule_name
            )

        # Placeholder - actual implementation would use event counts
        # This demonstrates the pure logic structure
        return RuleResult(
            fired=False,
            reason=f"Rate limit check needed for {scope} in {time_window}min (max: {max_events})",
            risk_score=0.0,
            rule_name=rule_name
        )

    def _evaluate_velocity_rule(
        self,
        rule_name: str,
        conditions: Dict[str, Any],
        event: EventContext,
        profile: Optional[ProfileContext]
    ) -> RuleResult:
        """Evaluate velocity rule (pure logic)"""
        time_window = conditions.get("time_window_minutes", 60)
        max_velocity = conditions.get("max_velocity", 10)
        scope = conditions.get("scope", "profile")

        if scope == "profile" and not profile:
            return RuleResult(
                fired=False,
                reason="No profile for velocity check",
                risk_score=0.0,
                rule_name=rule_name
            )

        # Placeholder - actual implementation would use event counts
        return RuleResult(
            fired=False,
            reason=f"Velocity check needed for {scope} in {time_window}min (max: {max_velocity})",
            risk_score=0.0,
            rule_name=rule_name
        )

    def _evaluate_device_rule(
        self,
        rule_name: str,
        conditions: Dict[str, Any],
        event: EventContext,
        profile: Optional[ProfileContext]
    ) -> RuleResult:
        """Evaluate device fingerprinting rule (pure logic)"""
        if not event.device_fingerprint:
            return RuleResult(
                fired=False,
                reason="No device fingerprint available",
                risk_score=0.0,
                rule_name=rule_name
            )

        check_device_reuse = conditions.get("check_device_reuse", False)
        max_device_uses = conditions.get("max_device_uses", 5)

        if check_device_reuse:
            # Placeholder - actual implementation would use device usage counts
            return RuleResult(
                fired=False,
                reason=f"Device reuse check needed (max: {max_device_uses})",
                risk_score=0.0,
                rule_name=rule_name
            )

        return RuleResult(
            fired=False,
            reason="Device fingerprint OK",
            risk_score=0.0,
            rule_name=rule_name
        )

    def _evaluate_custom_rule(
        self,
        rule_name: str,
        conditions: Dict[str, Any],
        event: EventContext,
        profile: Optional[ProfileContext]
    ) -> RuleResult:
        """Evaluate custom rule (pure logic)"""
        if not conditions.get("check_event_data", False):
            return RuleResult(
                fired=False,
                reason="Custom rule conditions not met",
                risk_score=0.0,
                rule_name=rule_name
            )

        suspicious_keywords = conditions.get("suspicious_keywords", [])
        if not suspicious_keywords:
            return RuleResult(
                fired=False,
                reason="No suspicious keywords configured",
                risk_score=0.0,
                rule_name=rule_name
            )

        # Check for suspicious patterns in event data
        for key, value in event.event_data.items():
            if isinstance(value, str):
                for keyword in suspicious_keywords:
                    if keyword.lower() in value.lower():
                        return RuleResult(
                            fired=True,
                            reason=f"Suspicious keyword detected: {keyword}",
                            risk_score=0.6,
                            rule_name=rule_name
                        )

        return RuleResult(
            fired=False,
            reason="Custom rule conditions not met",
            risk_score=0.0,
            rule_name=rule_name
        )

    def make_decision(
        self,
        rule_results: List[RuleResult],
        event: EventContext,
        customer_segment: str = "new_user",
        current_fpr: float = 0.01
    ) -> DecisionResult:
        """
        Make final decision using table-driven decision matrix

        Args:
            rule_results: List of rule evaluation results
            event: Event context
            customer_segment: Customer segment for decision matrix lookup
            current_fpr: Current false positive rate

        Returns:
            Final decision result
        """
        # Calculate risk score from rule results
        risk_score = self._calculate_risk_score(rule_results)
        risk_band = self._get_risk_band(risk_score)

        # Use decision matrix for final decision
        decision_result = self.decision_matrix.decide(
            event=event,
            risk_band=risk_band,
            customer_segment=customer_segment,
            current_fpr=current_fpr
        )

        # Add rule-specific information
        fired_rules = [r.rule_name for r in rule_results if r.fired]
        rule_reasons = [r.reason for r in rule_results if r.fired]

        # Combine reasons
        all_reasons = decision_result.reasons + rule_reasons

        return DecisionResult(
            decision=decision_result.action,
            risk_score=risk_score,
            reasons=all_reasons,
            rules_fired=fired_rules,
            metadata={
                **decision_result.metadata,
                "evaluated_at": event.created_at,
                "event_type": event.event_type,
                "profile_id": event.profile_id,
                "risk_band": risk_band.value,
                "customer_segment": customer_segment
            }
        )

    def _calculate_risk_score(self, rule_results: List[RuleResult]) -> float:
        """Calculate overall risk score from rule results"""
        if not rule_results:
            return 0.0

        # Use the highest risk score from fired rules
        max_risk = max((r.risk_score for r in rule_results if r.fired), default=0.0)

        # Apply weighted scoring if multiple rules fired
        fired_rules = [r for r in rule_results if r.fired]
        if len(fired_rules) > 1:
            # Increase risk score for multiple rule violations
            multiplier = min(1.2, 1.0 + (len(fired_rules) - 1) * 0.1)
            max_risk = min(1.0, max_risk * multiplier)

        return max_risk

    def _get_risk_band(self, risk_score: float) -> str:
        """Convert risk score to risk band"""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "med"
        elif risk_score < 0.8:
            return "high"
        else:
            return "critical"

    def _get_matrix_key(self, event_type: str, risk_band: str, customer_segment: str) -> str:
        """Generate matrix key for decision lookup"""
        return f"{event_type}:{risk_band}:{customer_segment}"

    def _create_rule_result(self, fired: bool, reason: str, risk_score: float, rule_name: str) -> RuleResult:
        """Helper method to create rule results for testing"""
        return RuleResult(
            fired=fired,
            reason=reason,
            risk_score=risk_score,
            rule_name=rule_name
        )
