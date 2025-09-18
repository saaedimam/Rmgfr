"""
Table-driven rule engine for fraud detection
Crystallizes complex conditional logic into clear, data-driven patterns
"""

from typing import List, Dict, Any, Optional, Callable, Protocol
from dataclasses import dataclass
from enum import Enum
import logging

from .decision_core import EventContext, ProfileContext, RuleResult, RuleType

logger = logging.getLogger(__name__)

class RuleAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"
    STEP_UP = "step_up"

@dataclass
class RuleDefinition:
    """Definition of a fraud detection rule"""
    name: str
    rule_type: RuleType
    conditions: Dict[str, Any]
    action: RuleAction
    priority: int
    enabled: bool = True
    description: str = ""

@dataclass
class RuleEvaluationContext:
    """Context for rule evaluation with all necessary data"""
    event: EventContext
    profile: Optional[ProfileContext]
    event_counts: Dict[str, int]  # Pre-calculated event counts
    device_usage_count: int
    ip_geolocation: Optional[Dict[str, Any]]
    user_behavior_score: float

class RuleEvaluator(Protocol):
    """Protocol for rule evaluators"""
    def evaluate(self, rule: RuleDefinition, context: RuleEvaluationContext) -> RuleResult:
        ...

class RateLimitEvaluator:
    """Evaluates rate limiting rules using table-driven logic"""

    def evaluate(self, rule: RuleDefinition, context: RuleEvaluationContext) -> RuleResult:
        conditions = rule.conditions
        scope = conditions.get("scope", "ip")
        time_window = conditions.get("time_window_minutes", 60)
        max_events = conditions.get("max_events", 100)

        # Guard clause: validate scope
        if scope not in ["ip", "profile", "device"]:
            return RuleResult(
                fired=False,
                reason=f"Invalid rate limit scope: {scope}",
                risk_score=0.0,
                rule_name=rule.name
            )

        # Get event count based on scope
        event_count = self._get_event_count_for_scope(scope, context)

        if event_count > max_events:
            risk_score = min(0.9, event_count / max_events)
            return RuleResult(
                fired=True,
                reason=f"Rate limit exceeded: {event_count} events in {time_window} minutes",
                risk_score=risk_score,
                rule_name=rule.name
            )

        return RuleResult(
            fired=False,
            reason=f"Rate limit OK: {event_count}/{max_events} events",
            risk_score=0.0,
            rule_name=rule.name
        )

    def _get_event_count_for_scope(self, scope: str, context: RuleEvaluationContext) -> int:
        """Get event count for specific scope"""
        if scope == "ip":
            return context.event_counts.get("ip", 0)
        elif scope == "profile" and context.profile:
            return context.event_counts.get("profile", 0)
        elif scope == "device":
            return context.event_counts.get("device", 0)
        return 0

class VelocityEvaluator:
    """Evaluates velocity rules using table-driven logic"""

    def evaluate(self, rule: RuleDefinition, context: RuleEvaluationContext) -> RuleResult:
        conditions = rule.conditions
        scope = conditions.get("scope", "profile")
        time_window = conditions.get("time_window_minutes", 60)
        max_velocity = conditions.get("max_velocity", 10)

        # Guard clause: validate scope
        if scope != "profile" or not context.profile:
            return RuleResult(
                fired=False,
                reason="Velocity check requires profile scope",
                risk_score=0.0,
                rule_name=rule.name
            )

        # Get velocity count
        velocity_count = context.event_counts.get("profile_velocity", 0)

        if velocity_count > max_velocity:
            risk_score = min(0.8, velocity_count / max_velocity)
            return RuleResult(
                fired=True,
                reason=f"Velocity exceeded: {velocity_count} events in {time_window} minutes",
                risk_score=risk_score,
                rule_name=rule.name
            )

        return RuleResult(
            fired=False,
            reason=f"Velocity OK: {velocity_count}/{max_velocity} events",
            risk_score=0.0,
            rule_name=rule.name
        )

class DeviceEvaluator:
    """Evaluates device fingerprinting rules using table-driven logic"""

    def evaluate(self, rule: RuleDefinition, context: RuleEvaluationContext) -> RuleResult:
        conditions = rule.conditions

        # Guard clause: check device fingerprint
        if not context.event.device_fingerprint:
            return RuleResult(
                fired=False,
                reason="No device fingerprint available",
                risk_score=0.0,
                rule_name=rule.name
            )

        # Check device reuse patterns
        if conditions.get("check_device_reuse", False):
            max_device_uses = conditions.get("max_device_uses", 5)

            if context.device_usage_count > max_device_uses:
                risk_score = min(0.7, context.device_usage_count / 10)
                return RuleResult(
                    fired=True,
                    reason=f"Device overuse: {context.device_usage_count} events from same device",
                    risk_score=risk_score,
                    rule_name=rule.name
                )

        return RuleResult(
            fired=False,
            reason="Device fingerprint OK",
            risk_score=0.0,
            rule_name=rule.name
        )

class CustomEvaluator:
    """Evaluates custom rules using table-driven logic"""

    def evaluate(self, rule: RuleDefinition, context: RuleEvaluationContext) -> RuleResult:
        conditions = rule.conditions

        # Guard clause: check if custom rule is enabled
        if not conditions.get("check_event_data", False):
            return RuleResult(
                fired=False,
                reason="Custom rule conditions not met",
                risk_score=0.0,
                rule_name=rule.name
            )

        # Check for suspicious keywords
        suspicious_keywords = conditions.get("suspicious_keywords", [])
        if not suspicious_keywords:
            return RuleResult(
                fired=False,
                reason="No suspicious keywords configured",
                risk_score=0.0,
                rule_name=rule.name
            )

        # Search for suspicious patterns
        for key, value in context.event.event_data.items():
            if isinstance(value, str):
                for keyword in suspicious_keywords:
                    if keyword.lower() in value.lower():
                        return RuleResult(
                            fired=True,
                            reason=f"Suspicious keyword detected: {keyword}",
                            risk_score=0.6,
                            rule_name=rule.name
                        )

        return RuleResult(
            fired=False,
            reason="Custom rule conditions not met",
            risk_score=0.0,
            rule_name=rule.name
        )

class GeolocationEvaluator:
    """Evaluates geolocation rules using table-driven logic"""

    def evaluate(self, rule: RuleDefinition, context: RuleEvaluationContext) -> RuleResult:
        conditions = rule.conditions

        # Guard clause: check if geolocation data is available
        if not context.ip_geolocation:
            return RuleResult(
                fired=False,
                reason="No geolocation data available",
                risk_score=0.0,
                rule_name=rule.name
            )

        # Check for VPN detection
        if conditions.get("enable_vpn_detection", False):
            if context.ip_geolocation.get("is_vpn", False):
                return RuleResult(
                    fired=True,
                    reason="VPN detected",
                    risk_score=0.5,
                    rule_name=rule.name
                )

        # Check for location consistency
        if conditions.get("enable_location_consistency", False):
            max_changes = conditions.get("max_location_changes", 3)
            location_changes = context.ip_geolocation.get("location_changes", 0)

            if location_changes > max_changes:
                risk_score = min(0.6, location_changes / 10)
                return RuleResult(
                    fired=True,
                    reason=f"Too many location changes: {location_changes}",
                    risk_score=risk_score,
                    rule_name=rule.name
                )

        return RuleResult(
            fired=False,
            reason="Geolocation checks passed",
            risk_score=0.0,
            rule_name=rule.name
        )

class BehaviorEvaluator:
    """Evaluates behavioral rules using table-driven logic"""

    def evaluate(self, rule: RuleDefinition, context: RuleEvaluationContext) -> RuleResult:
        conditions = rule.conditions

        # Guard clause: check if behavioral analysis is enabled
        if not conditions.get("enable_behavioral_analysis", False):
            return RuleResult(
                fired=False,
                reason="Behavioral analysis not enabled",
                risk_score=0.0,
                rule_name=rule.name
            )

        # Check behavior score threshold
        behavior_threshold = conditions.get("behavior_threshold", 0.7)

        if context.user_behavior_score > behavior_threshold:
            risk_score = min(0.8, context.user_behavior_score)
            return RuleResult(
                fired=True,
                reason=f"Unusual behavior detected: score {context.user_behavior_score:.2f}",
                risk_score=risk_score,
                rule_name=rule.name
            )

        return RuleResult(
            fired=False,
            reason=f"Behavior normal: score {context.user_behavior_score:.2f}",
            risk_score=0.0,
            rule_name=rule.name
        )

class TableDrivenRuleEngine:
    """
    Table-driven rule engine that replaces complex conditional logic
    with clear, data-driven patterns
    """

    def __init__(self):
        # Registry of rule evaluators
        self.evaluators: Dict[RuleType, RuleEvaluator] = {
            RuleType.RATE_LIMIT: RateLimitEvaluator(),
            RuleType.VELOCITY: VelocityEvaluator(),
            RuleType.DEVICE: DeviceEvaluator(),
            RuleType.CUSTOM: CustomEvaluator(),
        }

        # Extended evaluators for advanced rules
        self.extended_evaluators: Dict[str, RuleEvaluator] = {
            "geolocation": GeolocationEvaluator(),
            "behavior": BehaviorEvaluator(),
        }

    def evaluate_rules(
        self,
        rules: List[RuleDefinition],
        context: RuleEvaluationContext
    ) -> List[RuleResult]:
        """
        Evaluate all rules using table-driven logic

        Args:
            rules: List of rule definitions
            context: Evaluation context with all necessary data

        Returns:
            List of rule evaluation results
        """
        results = []

        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)

        for rule in sorted_rules:
            if not rule.enabled:
                continue

            try:
                result = self._evaluate_single_rule(rule, context)
                results.append(result)
            except Exception as e:
                logger.warning(f"Rule evaluation failed for {rule.name}: {e}")
                results.append(RuleResult(
                    fired=False,
                    reason=f"Rule evaluation error: {str(e)}",
                    risk_score=0.0,
                    rule_name=rule.name
                ))

        return results

    def _evaluate_single_rule(
        self,
        rule: RuleDefinition,
        context: RuleEvaluationContext
    ) -> RuleResult:
        """Evaluate a single rule using the appropriate evaluator"""

        # Check standard evaluators first
        if rule.rule_type in self.evaluators:
            evaluator = self.evaluators[rule.rule_type]
            return evaluator.evaluate(rule, context)

        # Check extended evaluators
        rule_type_str = rule.rule_type.value
        if rule_type_str in self.extended_evaluators:
            evaluator = self.extended_evaluators[rule_type_str]
            return evaluator.evaluate(rule, context)

        # Fallback for unknown rule types
        return RuleResult(
            fired=False,
            reason=f"Unknown rule type: {rule.rule_type}",
            risk_score=0.0,
            rule_name=rule.name
        )

    def register_evaluator(self, rule_type: str, evaluator: RuleEvaluator):
        """Register a custom rule evaluator"""
        self.extended_evaluators[rule_type] = evaluator

    def get_rule_definitions_from_config(self, config: Dict[str, Any]) -> List[RuleDefinition]:
        """Convert configuration to rule definitions"""
        rules = []

        for rule_config in config.get("rules", []):
            rule = RuleDefinition(
                name=rule_config["name"],
                rule_type=RuleType(rule_config["rule_type"]),
                conditions=rule_config.get("conditions", {}),
                action=RuleAction(rule_config.get("action", "review")),
                priority=rule_config.get("priority", 0),
                enabled=rule_config.get("enabled", True),
                description=rule_config.get("description", "")
            )
            rules.append(rule)

        return rules
