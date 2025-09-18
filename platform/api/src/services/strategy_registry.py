"""
Strategy Registry for composable fraud detection rules
Elevates the system with flexible, composable patterns
"""

from typing import Dict, List, Any, Optional, Protocol, Type, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from .decision_core import EventContext, ProfileContext, RuleResult, RiskBand

logger = logging.getLogger(__name__)

class RuleStrategy(Protocol):
    """Protocol for rule strategies"""
    def evaluate(self, context: 'RuleEvaluationContext') -> RuleResult:
        ...

class RuleEvaluationContext:
    """Enhanced context for rule evaluation"""
    def __init__(
        self,
        event: EventContext,
        profile: Optional[ProfileContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.event = event
        self.profile = profile
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

class ComposableRule(ABC):
    """Base class for composable rules"""

    def __init__(self, name: str, priority: int = 0, enabled: bool = True):
        self.name = name
        self.priority = priority
        self.enabled = enabled
        self.created_at = datetime.utcnow()

    @abstractmethod
    def evaluate(self, context: RuleEvaluationContext) -> RuleResult:
        """Evaluate the rule"""
        pass

    def can_compose_with(self, other: 'ComposableRule') -> bool:
        """Check if this rule can be composed with another"""
        return True

    def get_dependencies(self) -> List[str]:
        """Get list of rule dependencies"""
        return []

    def get_metadata(self) -> Dict[str, Any]:
        """Get rule metadata"""
        return {
            'name': self.name,
            'priority': self.priority,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'dependencies': self.get_dependencies()
        }

class RuleComposition:
    """Represents a composition of rules"""

    def __init__(self, rules: List[ComposableRule], operator: str = 'AND'):
        self.rules = rules
        self.operator = operator
        self.name = f"Composition({operator})"

    def evaluate(self, context: RuleEvaluationContext) -> RuleResult:
        """Evaluate the composition"""
        results = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            try:
                result = rule.evaluate(context)
                results.append(result)
            except Exception as e:
                logger.warning(f"Rule {rule.name} evaluation failed: {e}")
                results.append(RuleResult(
                    fired=False,
                    reason=f"Rule evaluation error: {str(e)}",
                    risk_score=0.0,
                    rule_name=rule.name
                ))

        if self.operator == 'AND':
            return self._evaluate_and(results)
        elif self.operator == 'OR':
            return self._evaluate_or(results)
        elif self.operator == 'MAJORITY':
            return self._evaluate_majority(results)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    def _evaluate_and(self, results: List[RuleResult]) -> RuleResult:
        """All rules must fire for composition to fire"""
        fired_rules = [r for r in results if r.fired]

        if len(fired_rules) == len(results) and len(results) > 0:
            # All rules fired
            max_risk = max(r.risk_score for r in fired_rules)
            reasons = [r.reason for r in fired_rules]
            rule_names = [r.rule_name for r in fired_rules]

            return RuleResult(
                fired=True,
                reason=f"All rules fired: {', '.join(rule_names)}",
                risk_score=max_risk,
                rule_name=f"AND({', '.join(rule_names)})"
            )
        else:
            return RuleResult(
                fired=False,
                reason="Not all rules fired",
                risk_score=0.0,
                rule_name=self.name
            )

    def _evaluate_or(self, results: List[RuleResult]) -> RuleResult:
        """Any rule can fire for composition to fire"""
        fired_rules = [r for r in results if r.fired]

        if fired_rules:
            max_risk = max(r.risk_score for r in fired_rules)
            reasons = [r.reason for r in fired_rules]
            rule_names = [r.rule_name for r in fired_rules]

            return RuleResult(
                fired=True,
                reason=f"Any rule fired: {', '.join(rule_names)}",
                risk_score=max_risk,
                rule_name=f"OR({', '.join(rule_names)})"
            )
        else:
            return RuleResult(
                fired=False,
                reason="No rules fired",
                risk_score=0.0,
                rule_name=self.name
            )

    def _evaluate_majority(self, results: List[RuleResult]) -> RuleResult:
        """Majority of rules must fire for composition to fire"""
        fired_rules = [r for r in results if r.fired]
        threshold = len(results) / 2

        if len(fired_rules) > threshold:
            avg_risk = sum(r.risk_score for r in fired_rules) / len(fired_rules)
            reasons = [r.reason for r in fired_rules]
            rule_names = [r.rule_name for r in fired_rules]

            return RuleResult(
                fired=True,
                reason=f"Majority rules fired: {', '.join(rule_names)}",
                risk_score=avg_risk,
                rule_name=f"MAJORITY({', '.join(rule_names)})"
            )
        else:
            return RuleResult(
                fired=False,
                reason="Majority of rules did not fire",
                risk_score=0.0,
                rule_name=self.name
            )

class StrategyRegistry:
    """Registry for managing rule strategies and compositions"""

    def __init__(self):
        self.strategies: Dict[str, Type[ComposableRule]] = {}
        self.compositions: Dict[str, RuleComposition] = {}
        self.rule_instances: Dict[str, ComposableRule] = {}

    def register_strategy(self, name: str, strategy_class: Type[ComposableRule]):
        """Register a rule strategy"""
        self.strategies[name] = strategy_class
        logger.info(f"Registered strategy: {name}")

    def create_rule(self, name: str, strategy_name: str, **kwargs) -> ComposableRule:
        """Create a rule instance from a strategy"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        strategy_class = self.strategies[strategy_name]
        rule = strategy_class(name=name, **kwargs)
        self.rule_instances[name] = rule

        logger.info(f"Created rule: {name} using strategy: {strategy_name}")
        return rule

    def create_composition(
        self,
        name: str,
        rule_names: List[str],
        operator: str = 'AND'
    ) -> RuleComposition:
        """Create a rule composition"""
        rules = [self.rule_instances[name] for name in rule_names if name in self.rule_instances]

        if not rules:
            raise ValueError("No valid rules found for composition")

        composition = RuleComposition(rules, operator)
        self.compositions[name] = composition

        logger.info(f"Created composition: {name} with {len(rules)} rules using {operator}")
        return composition

    def evaluate_rule(self, rule_name: str, context: RuleEvaluationContext) -> RuleResult:
        """Evaluate a single rule or composition"""
        if rule_name in self.rule_instances:
            return self.rule_instances[rule_name].evaluate(context)
        elif rule_name in self.compositions:
            return self.compositions[rule_name].evaluate(context)
        else:
            raise ValueError(f"Unknown rule: {rule_name}")

    def evaluate_all_rules(self, context: RuleEvaluationContext) -> List[RuleResult]:
        """Evaluate all enabled rules and compositions"""
        results = []

        # Evaluate individual rules
        for rule in self.rule_instances.values():
            if rule.enabled:
                try:
                    result = rule.evaluate(context)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Rule {rule.name} evaluation failed: {e}")
                    results.append(RuleResult(
                        fired=False,
                        reason=f"Rule evaluation error: {str(e)}",
                        risk_score=0.0,
                        rule_name=rule.name
                    ))

        # Evaluate compositions
        for composition in self.compositions.values():
            try:
                result = composition.evaluate(context)
                results.append(result)
            except Exception as e:
                logger.warning(f"Composition evaluation failed: {e}")
                results.append(RuleResult(
                    fired=False,
                    reason=f"Composition evaluation error: {str(e)}",
                    risk_score=0.0,
                    rule_name=composition.name
                ))

        return results

    def get_rule_metadata(self) -> Dict[str, Any]:
        """Get metadata for all rules and compositions"""
        metadata = {
            'strategies': list(self.strategies.keys()),
            'rules': {name: rule.get_metadata() for name, rule in self.rule_instances.items()},
            'compositions': {
                name: {
                    'operator': comp.operator,
                    'rules': [rule.name for rule in comp.rules]
                }
                for name, comp in self.compositions.items()
            }
        }
        return metadata

# Concrete rule implementations
class VelocityRule(ComposableRule):
    """Velocity-based fraud detection rule"""

    def __init__(self, name: str, max_events: int, time_window_minutes: int, **kwargs):
        super().__init__(name, **kwargs)
        self.max_events = max_events
        self.time_window_minutes = time_window_minutes

    def evaluate(self, context: RuleEvaluationContext) -> RuleResult:
        # This would use actual event counts from the data service
        event_count = context.metadata.get('event_count', 0)

        if event_count > self.max_events:
            risk_score = min(0.9, event_count / self.max_events)
            return RuleResult(
                fired=True,
                reason=f"Velocity exceeded: {event_count} events in {self.time_window_minutes} minutes",
                risk_score=risk_score,
                rule_name=self.name
            )

        return RuleResult(
            fired=False,
            reason=f"Velocity OK: {event_count}/{self.max_events} events",
            risk_score=0.0,
            rule_name=self.name
        )

class DeviceFingerprintRule(ComposableRule):
    """Device fingerprint-based fraud detection rule"""

    def __init__(self, name: str, max_device_uses: int, **kwargs):
        super().__init__(name, **kwargs)
        self.max_device_uses = max_device_uses

    def evaluate(self, context: RuleEvaluationContext) -> RuleResult:
        if not context.event.device_fingerprint:
            return RuleResult(
                fired=False,
                reason="No device fingerprint available",
                risk_score=0.0,
                rule_name=self.name
            )

        device_usage_count = context.metadata.get('device_usage_count', 0)

        if device_usage_count > self.max_device_uses:
            risk_score = min(0.7, device_usage_count / 10)
            return RuleResult(
                fired=True,
                reason=f"Device overuse: {device_usage_count} events from same device",
                risk_score=risk_score,
                rule_name=self.name
            )

        return RuleResult(
            fired=False,
            reason="Device fingerprint OK",
            risk_score=0.0,
            rule_name=self.name
        )

class AmountRule(ComposableRule):
    """Transaction amount-based fraud detection rule"""

    def __init__(self, name: str, max_amount: float, **kwargs):
        super().__init__(name, **kwargs)
        self.max_amount = max_amount

    def evaluate(self, context: RuleEvaluationContext) -> RuleResult:
        amount = context.event.amount or 0

        if amount > self.max_amount:
            risk_score = min(0.8, amount / self.max_amount)
            return RuleResult(
                fired=True,
                reason=f"Amount exceeds limit: ${amount} > ${self.max_amount}",
                risk_score=risk_score,
                rule_name=self.name
            )

        return RuleResult(
            fired=False,
            reason=f"Amount OK: ${amount} <= ${self.max_amount}",
            risk_score=0.0,
            rule_name=self.name
        )

# Global registry instance
registry = StrategyRegistry()

# Register default strategies
registry.register_strategy('velocity', VelocityRule)
registry.register_strategy('device_fingerprint', DeviceFingerprintRule)
registry.register_strategy('amount', AmountRule)
