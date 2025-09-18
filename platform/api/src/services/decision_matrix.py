"""
Configuration-driven decision matrix
Crystallizes decision logic into clear, data-driven patterns
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging

from .decision_core import EventContext, DecisionResult, RiskBand

logger = logging.getLogger(__name__)

class DecisionAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"
    STEP_UP = "step_up"

@dataclass
class DecisionMatrixEntry:
    """Single entry in the decision matrix"""
    event_type: str
    risk_band: RiskBand
    customer_segment: str
    action: DecisionAction
    max_fpr: float
    confidence_threshold: float
    notes: str = ""

@dataclass
class DecisionMatrixConfig:
    """Configuration for the decision matrix"""
    entries: List[DecisionMatrixEntry]
    default_action: DecisionAction = DecisionAction.REVIEW
    default_max_fpr: float = 0.01
    fpr_escalation_threshold: float = 0.8

class DecisionMatrixEngine:
    """
    Configuration-driven decision matrix engine
    Replaces hard-coded decision logic with data-driven patterns
    """

    def __init__(self, config: DecisionMatrixConfig):
        self.config = config
        self.matrix = self._build_matrix_lookup()

    def _build_matrix_lookup(self) -> Dict[str, DecisionMatrixEntry]:
        """Build fast lookup table for decision matrix"""
        matrix = {}

        for entry in self.config.entries:
            key = self._generate_matrix_key(
                entry.event_type,
                entry.risk_band,
                entry.customer_segment
            )
            matrix[key] = entry

        return matrix

    def _generate_matrix_key(
        self,
        event_type: str,
        risk_band: RiskBand,
        customer_segment: str
    ) -> str:
        """Generate lookup key for decision matrix"""
        return f"{event_type}:{risk_band.value}:{customer_segment}"

    def decide(
        self,
        event: EventContext,
        risk_band: RiskBand,
        customer_segment: str,
        current_fpr: float
    ) -> DecisionResult:
        """
        Make decision using configuration-driven matrix

        Args:
            event: Event context
            risk_band: Calculated risk band
            customer_segment: Customer segment
            current_fpr: Current false positive rate

        Returns:
            Decision result
        """
        # Generate lookup key
        matrix_key = self._generate_matrix_key(
            event.event_type,
            risk_band,
            customer_segment
        )

        # Get matrix entry or use default
        matrix_entry = self.matrix.get(matrix_key)

        if not matrix_entry:
            # Use default decision
            return self._create_default_decision(
                event, risk_band, customer_segment, current_fpr
            )

        # Check FPR escalation
        if current_fpr > matrix_entry.max_fpr:
            return self._create_fpr_escalation_decision(
                matrix_entry, current_fpr
            )

        # Normal decision flow
        return self._create_normal_decision(
            matrix_entry, event, risk_band, customer_segment
        )

    def _create_default_decision(
        self,
        event: EventContext,
        risk_band: RiskBand,
        customer_segment: str,
        current_fpr: float
    ) -> DecisionResult:
        """Create decision using default configuration"""
        return DecisionResult(
            action=self.config.default_action,
            confidence=1.0 - self._get_risk_score_from_band(risk_band),
            reasons=[
                f"Using default decision for {event.event_type}",
                f"Risk band: {risk_band.value}",
                f"Customer segment: {customer_segment}",
                f"Max FPR: {self.config.default_max_fpr:.3f}"
            ],
            rules_fired=["default_decision"],
            metadata={
                "matrix_key": self._generate_matrix_key(
                    event.event_type, risk_band, customer_segment
                ),
                "is_default": True
            }
        )

    def _create_fpr_escalation_decision(
        self,
        matrix_entry: DecisionMatrixEntry,
        current_fpr: float
    ) -> DecisionResult:
        """Create decision when FPR exceeds threshold"""
        return DecisionResult(
            action=DecisionAction.REVIEW,
            confidence=0.8,
            reasons=[
                f"FPR {current_fpr:.3f} exceeds threshold {matrix_entry.max_fpr:.3f}",
                f"Escalating {matrix_entry.action.value} to review"
            ],
            rules_fired=["fpr_escalation"],
            metadata={
                "original_action": matrix_entry.action.value,
                "fpr_threshold": matrix_entry.max_fpr,
                "current_fpr": current_fpr,
                "is_escalation": True
            }
        )

    def _create_normal_decision(
        self,
        matrix_entry: DecisionMatrixEntry,
        event: EventContext,
        risk_band: RiskBand,
        customer_segment: str
    ) -> DecisionResult:
        """Create normal decision based on matrix entry"""
        confidence = 1.0 - self._get_risk_score_from_band(risk_band)

        return DecisionResult(
            action=matrix_entry.action,
            confidence=confidence,
            reasons=[
                f"Risk band: {risk_band.value}",
                f"Customer segment: {customer_segment}",
                f"Action: {matrix_entry.action.value}",
                f"Max FPR: {matrix_entry.max_fpr:.3f}",
                f"Confidence threshold: {matrix_entry.confidence_threshold:.3f}"
            ],
            rules_fired=[f"matrix_{matrix_entry.event_type}_{risk_band.value}"],
            metadata={
                "matrix_key": self._generate_matrix_key(
                    event.event_type, risk_band, customer_segment
                ),
                "confidence_threshold": matrix_entry.confidence_threshold,
                "is_normal": True
            }
        )

    def _get_risk_score_from_band(self, risk_band: RiskBand) -> float:
        """Convert risk band to numeric score"""
        band_scores = {
            RiskBand.LOW: 0.2,
            RiskBand.MED: 0.5,
            RiskBand.HIGH: 0.7,
            RiskBand.CRITICAL: 0.9
        }
        return band_scores.get(risk_band, 0.5)

    def add_matrix_entry(self, entry: DecisionMatrixEntry):
        """Add new matrix entry at runtime"""
        key = self._generate_matrix_key(
            entry.event_type,
            entry.risk_band,
            entry.customer_segment
        )
        self.matrix[key] = entry
        logger.info(f"Added matrix entry: {key}")

    def remove_matrix_entry(
        self,
        event_type: str,
        risk_band: RiskBand,
        customer_segment: str
    ):
        """Remove matrix entry at runtime"""
        key = self._generate_matrix_key(event_type, risk_band, customer_segment)
        if key in self.matrix:
            del self.matrix[key]
            logger.info(f"Removed matrix entry: {key}")

    def get_matrix_entries(self) -> List[DecisionMatrixEntry]:
        """Get all matrix entries"""
        return list(self.matrix.values())

    def export_config(self) -> Dict:
        """Export current configuration"""
        return {
            "entries": [
                {
                    "event_type": entry.event_type,
                    "risk_band": entry.risk_band.value,
                    "customer_segment": entry.customer_segment,
                    "action": entry.action.value,
                    "max_fpr": entry.max_fpr,
                    "confidence_threshold": entry.confidence_threshold,
                    "notes": entry.notes
                }
                for entry in self.matrix.values()
            ],
            "default_action": self.config.default_action.value,
            "default_max_fpr": self.config.default_max_fpr,
            "fpr_escalation_threshold": self.config.fpr_escalation_threshold
        }

class DecisionMatrixFactory:
    """Factory for creating decision matrix configurations"""

    @staticmethod
    def create_default_config() -> DecisionMatrixConfig:
        """Create default decision matrix configuration"""
        entries = [
            # Low risk entries
            DecisionMatrixEntry(
                event_type="login",
                risk_band=RiskBand.LOW,
                customer_segment="new_user",
                action=DecisionAction.ALLOW,
                max_fpr=0.01,
                confidence_threshold=0.8,
                notes="New user login with low risk"
            ),
            DecisionMatrixEntry(
                event_type="login",
                risk_band=RiskBand.LOW,
                customer_segment="returning",
                action=DecisionAction.ALLOW,
                max_fpr=0.005,
                confidence_threshold=0.9,
                notes="Returning user login with low risk"
            ),

            # Medium risk entries
            DecisionMatrixEntry(
                event_type="payment",
                risk_band=RiskBand.MED,
                customer_segment="new_user",
                action=DecisionAction.STEP_UP,
                max_fpr=0.008,
                confidence_threshold=0.7,
                notes="New user payment with medium risk"
            ),
            DecisionMatrixEntry(
                event_type="payment",
                risk_band=RiskBand.MED,
                customer_segment="returning",
                action=DecisionAction.ALLOW,
                max_fpr=0.003,
                confidence_threshold=0.8,
                notes="Returning user payment with medium risk"
            ),

            # High risk entries
            DecisionMatrixEntry(
                event_type="payment",
                risk_band=RiskBand.HIGH,
                customer_segment="new_user",
                action=DecisionAction.REVIEW,
                max_fpr=0.005,
                confidence_threshold=0.6,
                notes="New user payment with high risk"
            ),
            DecisionMatrixEntry(
                event_type="payment",
                risk_band=RiskBand.HIGH,
                customer_segment="returning",
                action=DecisionAction.STEP_UP,
                max_fpr=0.002,
                confidence_threshold=0.7,
                notes="Returning user payment with high risk"
            ),

            # Critical risk entries
            DecisionMatrixEntry(
                event_type="payment",
                risk_band=RiskBand.CRITICAL,
                customer_segment="new_user",
                action=DecisionAction.DENY,
                max_fpr=0.001,
                confidence_threshold=0.5,
                notes="New user payment with critical risk"
            ),
            DecisionMatrixEntry(
                event_type="payment",
                risk_band=RiskBand.CRITICAL,
                customer_segment="returning",
                action=DecisionAction.REVIEW,
                max_fpr=0.001,
                confidence_threshold=0.6,
                notes="Returning user payment with critical risk"
            ),
        ]

        return DecisionMatrixConfig(
            entries=entries,
            default_action=DecisionAction.REVIEW,
            default_max_fpr=0.01,
            fpr_escalation_threshold=0.8
        )

    @staticmethod
    def create_from_json(config_data: Dict) -> DecisionMatrixConfig:
        """Create configuration from JSON data"""
        entries = []

        for entry_data in config_data.get("entries", []):
            entry = DecisionMatrixEntry(
                event_type=entry_data["event_type"],
                risk_band=RiskBand(entry_data["risk_band"]),
                customer_segment=entry_data["customer_segment"],
                action=DecisionAction(entry_data["action"]),
                max_fpr=entry_data["max_fpr"],
                confidence_threshold=entry_data.get("confidence_threshold", 0.8),
                notes=entry_data.get("notes", "")
            )
            entries.append(entry)

        return DecisionMatrixConfig(
            entries=entries,
            default_action=DecisionAction(
                config_data.get("default_action", "review")
            ),
            default_max_fpr=config_data.get("default_max_fpr", 0.01),
            fpr_escalation_threshold=config_data.get("fpr_escalation_threshold", 0.8)
        )
