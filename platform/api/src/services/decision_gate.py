"""
Decision Gate Service
Implements the core decision logic for fraud detection
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class Action(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"
    STEP_UP = "step_up"

@dataclass
class DecisionMatrix:
    event_type: str
    risk_band: str
    customer_segment: str
    action: Action
    max_fpr: float
    notes: str

@dataclass
class DecisionContext:
    event_type: str
    risk_score: float
    customer_segment: str
    latest_fpr: float

class DecisionGate:
    """
    Core decision gate that determines fraud actions based on decision matrix
    """
    
    def __init__(self):
        self.decision_matrix: Dict[str, DecisionMatrix] = {}
        self._load_decision_matrix()
    
    def _load_decision_matrix(self):
        """Load decision matrix from database or cache"""
        # This would typically load from database
        # For now, we'll use a simple in-memory cache
        logger.info("Loading decision matrix...")
        # TODO: Load from database/cache
        pass
    
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
        """Generate key for decision matrix lookup"""
        return f"{event_type}:{risk_band}:{customer_segment}"
    
    def decide(self, context: DecisionContext, matrix_map: Optional[Dict] = None) -> Tuple[Action, float, List[str]]:
        """
        Core decision function
        
        Args:
            context: Decision context with event details
            matrix_map: Optional decision matrix override
            latest_fpr: Latest false positive rate for the action
            
        Returns:
            Tuple of (action, confidence, reasons)
        """
        try:
            # Get risk band from risk score
            risk_band = self._get_risk_band(context.risk_score)
            
            # Generate matrix key
            matrix_key = self._get_matrix_key(
                context.event_type,
                risk_band,
                context.customer_segment
            )
            
            # Use provided matrix or default
            if matrix_map and matrix_key in matrix_map:
                matrix_entry = matrix_map[matrix_key]
            else:
                # Fallback to default decision matrix
                matrix_entry = self._get_default_decision(context.event_type, risk_band, context.customer_segment)
            
            # Extract action and max FPR
            action = Action(matrix_entry.get('action', 'review'))
            max_fpr = matrix_entry.get('max_fpr', 0.01)
            
            # Check if current FPR exceeds threshold
            if context.latest_fpr > max_fpr:
                # FPR too high, escalate to review
                action = Action.REVIEW
                confidence = 0.8
                reasons = [
                    f"FPR {context.latest_fpr:.3f} exceeds threshold {max_fpr:.3f}",
                    f"Escalating {action.value} to review"
                ]
            else:
                # Normal decision flow
                confidence = 1.0 - context.risk_score
                reasons = [
                    f"Risk band: {risk_band}",
                    f"Customer segment: {context.customer_segment}",
                    f"Action: {action.value}",
                    f"Max FPR: {max_fpr:.3f}"
                ]
            
            logger.info(f"Decision: {action.value} for {matrix_key} (confidence: {confidence:.2f})")
            return action, confidence, reasons
            
        except Exception as e:
            logger.error(f"Error in decision gate: {e}")
            # Fail safe to review
            return Action.REVIEW, 0.5, [f"Error in decision logic: {str(e)}"]
    
    def _get_default_decision(self, event_type: str, risk_band: str, customer_segment: str) -> Dict:
        """Get default decision when matrix lookup fails"""
        # Default decision matrix based on risk level
        defaults = {
            "low": {"action": "allow", "max_fpr": 0.01},
            "med": {"action": "step_up", "max_fpr": 0.008},
            "high": {"action": "review", "max_fpr": 0.005},
            "critical": {"action": "deny", "max_fpr": 0.002}
        }
        
        return defaults.get(risk_band, {"action": "review", "max_fpr": 0.01})
    
    def update_matrix(self, matrix_data: List[Dict]):
        """Update decision matrix with new data"""
        logger.info(f"Updating decision matrix with {len(matrix_data)} entries")
        
        for entry in matrix_data:
            key = self._get_matrix_key(
                entry['event_type'],
                entry['risk_band'],
                entry['customer_segment']
            )
            
            self.decision_matrix[key] = DecisionMatrix(
                event_type=entry['event_type'],
                risk_band=entry['risk_band'],
                customer_segment=entry['customer_segment'],
                action=Action(entry['action']),
                max_fpr=float(entry['max_fpr']),
                notes=entry.get('notes', '')
            )
        
        logger.info("Decision matrix updated successfully")

# Global instance
decision_gate = DecisionGate()
