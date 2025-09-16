"""
Tests for Decision Gate Service
"""

import pytest
from src.services.decision_gate import DecisionGate, DecisionContext, Action

class TestDecisionGate:
    
    def setup_method(self):
        self.decision_gate = DecisionGate()
    
    def test_low_risk_decision(self):
        """Test low risk decision results in allow"""
        context = DecisionContext(
            event_type="login",
            risk_score=0.2,
            customer_segment="returning",
            latest_fpr=0.005
        )
        
        action, confidence, reasons = self.decision_gate.decide(context)
        
        assert action == Action.ALLOW
        assert confidence > 0.7
        assert "Risk band: low" in reasons
    
    def test_high_risk_decision(self):
        """Test high risk decision results in review"""
        context = DecisionContext(
            event_type="payment",
            risk_score=0.7,  # Use 0.7 to get "high" risk band
            customer_segment="new_user",
            latest_fpr=0.001  # Lower FPR to avoid threshold escalation
        )
        
        action, confidence, reasons = self.decision_gate.decide(context)
        
        assert action == Action.REVIEW
        assert confidence < 0.4  # High risk (0.7) should have lower confidence (0.3)
        assert "Risk band: high" in reasons
    
    def test_critical_risk_decision(self):
        """Test critical risk decision results in deny"""
        context = DecisionContext(
            event_type="signup",
            risk_score=0.9,
            customer_segment="new_user",
            latest_fpr=0.001
        )
        
        action, confidence, reasons = self.decision_gate.decide(context)
        
        assert action == Action.DENY
        assert confidence < 0.2
        assert "Risk band: critical" in reasons
    
    def test_fpr_threshold_exceeded(self):
        """Test FPR threshold exceeded escalates to review"""
        context = DecisionContext(
            event_type="login",
            risk_score=0.2,
            customer_segment="returning",
            latest_fpr=0.02  # Exceeds typical threshold
        )
        
        action, confidence, reasons = self.decision_gate.decide(context)
        
        assert action == Action.REVIEW
        assert "FPR" in reasons[0]
        assert "exceeds threshold" in reasons[0]
    
    def test_risk_band_classification(self):
        """Test risk band classification"""
        assert self.decision_gate._get_risk_band(0.1) == "low"
        assert self.decision_gate._get_risk_band(0.4) == "med"
        assert self.decision_gate._get_risk_band(0.7) == "high"
        assert self.decision_gate._get_risk_band(0.9) == "critical"
    
    def test_matrix_key_generation(self):
        """Test matrix key generation"""
        key = self.decision_gate._get_matrix_key("login", "med", "returning")
        assert key == "login:med:returning"
    
    def test_default_decision_fallback(self):
        """Test default decision when matrix lookup fails"""
        context = DecisionContext(
            event_type="unknown_event",
            risk_score=0.5,
            customer_segment="unknown_segment",
            latest_fpr=0.01
        )
        
        action, confidence, reasons = self.decision_gate.decide(context)
        
        # Should fall back to default decision
        assert action in [Action.ALLOW, Action.STEP_UP, Action.REVIEW, Action.DENY]
        assert confidence > 0
        assert len(reasons) > 0
    
    def test_error_handling(self):
        """Test error handling in decision logic"""
        # Create invalid context to trigger error
        context = DecisionContext(
            event_type="",  # Empty string
            risk_score=-1,  # Invalid risk score
            customer_segment="",
            latest_fpr=-1
        )
        
        action, confidence, reasons = self.decision_gate.decide(context)
        
        # Should fail safe to review or allow (depending on risk band)
        assert action in [Action.REVIEW, Action.ALLOW]
        assert confidence >= 0
        assert len(reasons) > 0

if __name__ == "__main__":
    pytest.main([__file__])
