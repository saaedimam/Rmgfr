"""
Unit tests for DecisionCore - pure business logic testing
"""

import pytest
from datetime import datetime
from src.services.decision_core import (
    DecisionCore,
    EventContext,
    ProfileContext,
    RuleType,
    RuleAction
)

class TestDecisionCore:
    """Test suite for DecisionCore pure business logic"""

    def setup_method(self):
        """Set up test fixtures"""
        self.decision_core = DecisionCore()

        # Sample event context
        self.event_context = EventContext(
            event_type="payment",
            event_data={"amount": 100.0, "currency": "USD"},
            profile_id="user123",
            device_fingerprint="device456",
            ip_address="192.168.1.1",
            amount=100.0,
            created_at=datetime.utcnow().isoformat(),
            project_id="project789"
        )

        # Sample profile context
        self.profile_context = ProfileContext(
            id="user123",
            created_at=datetime.utcnow().isoformat(),
            last_activity=datetime.utcnow().isoformat()
        )

    def test_risk_band_calculation(self):
        """Test risk band calculation logic"""
        # Test low risk
        risk_band = self.decision_core._get_risk_band(0.2)
        assert risk_band == "low"

        # Test medium risk
        risk_band = self.decision_core._get_risk_band(0.5)
        assert risk_band == "med"

        # Test high risk
        risk_band = self.decision_core._get_risk_band(0.7)
        assert risk_band == "high"

        # Test critical risk
        risk_band = self.decision_core._get_risk_band(0.9)
        assert risk_band == "critical"

    def test_custom_rule_evaluation_with_suspicious_keywords(self):
        """Test custom rule evaluation with suspicious keywords"""
        rule = {
            "name": "suspicious_keywords",
            "rule_type": "custom",
            "conditions": {
                "check_event_data": True,
                "suspicious_keywords": ["test", "fraud", "suspicious"]
            }
        }

        # Test with suspicious keyword
        suspicious_event = EventContext(
            event_type="payment",
            event_data={"description": "This is a test transaction"},
            profile_id="user123",
            device_fingerprint="device456",
            ip_address="192.168.1.1",
            amount=100.0,
            created_at=datetime.utcnow().isoformat(),
            project_id="project789"
        )

        result = self.decision_core._evaluate_single_rule(rule, suspicious_event, self.profile_context)

        assert result.fired is True
        assert "test" in result.reason
        assert result.risk_score == 0.6
        assert result.rule_name == "suspicious_keywords"

    def test_custom_rule_evaluation_without_suspicious_keywords(self):
        """Test custom rule evaluation without suspicious keywords"""
        rule = {
            "name": "suspicious_keywords",
            "rule_type": "custom",
            "conditions": {
                "check_event_data": True,
                "suspicious_keywords": ["fraud", "suspicious"]
            }
        }

        # Test with clean event data
        clean_event = EventContext(
            event_type="payment",
            event_data={"description": "Regular purchase"},
            profile_id="user123",
            device_fingerprint="device456",
            ip_address="192.168.1.1",
            amount=100.0,
            created_at=datetime.utcnow().isoformat(),
            project_id="project789"
        )

        result = self.decision_core._evaluate_single_rule(rule, clean_event, self.profile_context)

        assert result.fired is False
        assert "Custom rule conditions not met" in result.reason
        assert result.risk_score == 0.0

    def test_device_rule_evaluation_without_fingerprint(self):
        """Test device rule evaluation without device fingerprint"""
        rule = {
            "name": "device_check",
            "rule_type": "device",
            "conditions": {
                "check_device_reuse": True,
                "max_device_uses": 5
            }
        }

        # Test with no device fingerprint
        no_device_event = EventContext(
            event_type="payment",
            event_data={},
            profile_id="user123",
            device_fingerprint=None,
            ip_address="192.168.1.1",
            amount=100.0,
            created_at=datetime.utcnow().isoformat(),
            project_id="project789"
        )

        result = self.decision_core._evaluate_single_rule(rule, no_device_event, self.profile_context)

        assert result.fired is False
        assert "No device fingerprint available" in result.reason
        assert result.risk_score == 0.0

    def test_decision_making_with_no_fired_rules(self):
        """Test decision making when no rules fire"""
        rule_results = [
            self.decision_core._create_rule_result(False, "Rule 1 OK", 0.0, "rule1"),
            self.decision_core._create_rule_result(False, "Rule 2 OK", 0.0, "rule2")
        ]

        decision_result = self.decision_core.make_decision(rule_results, self.event_context)

        assert decision_result.decision == "allow"
        assert decision_result.risk_score == 0.0
        assert len(decision_result.reasons) == 0
        assert len(decision_result.rules_fired) == 0

    def test_decision_making_with_high_risk_rule(self):
        """Test decision making with high risk rule"""
        rule_results = [
            self.decision_core._create_rule_result(True, "High risk detected", 0.9, "high_risk_rule")
        ]

        decision_result = self.decision_core.make_decision(rule_results, self.event_context)

        assert decision_result.decision == "deny"
        assert decision_result.risk_score == 0.9
        assert len(decision_result.reasons) == 1
        assert "High risk detected" in decision_result.reasons
        assert "high_risk_rule" in decision_result.rules_fired

    def test_decision_making_with_medium_risk_rule(self):
        """Test decision making with medium risk rule"""
        rule_results = [
            self.decision_core._create_rule_result(True, "Medium risk detected", 0.7, "medium_risk_rule")
        ]

        decision_result = self.decision_core.make_decision(rule_results, self.event_context)

        assert decision_result.decision == "review"
        assert decision_result.risk_score == 0.7
        assert len(decision_result.reasons) == 1
        assert "Medium risk detected" in decision_result.reasons
        assert "medium_risk_rule" in decision_result.rules_fired

    def test_decision_making_with_multiple_rules(self):
        """Test decision making with multiple rules"""
        rule_results = [
            self.decision_core._create_rule_result(True, "Low risk detected", 0.3, "low_risk_rule"),
            self.decision_core._create_rule_result(True, "High risk detected", 0.9, "high_risk_rule"),
            self.decision_core._create_rule_result(False, "Rule OK", 0.0, "ok_rule")
        ]

        decision_result = self.decision_core.make_decision(rule_results, self.event_context)

        assert decision_result.decision == "deny"  # Highest risk wins
        assert decision_result.risk_score == 0.9
        assert len(decision_result.reasons) == 2  # Only fired rules
        assert len(decision_result.rules_fired) == 2
        assert "low_risk_rule" in decision_result.rules_fired
        assert "high_risk_rule" in decision_result.rules_fired
        assert "ok_rule" not in decision_result.rules_fired

    def test_risk_band_calculation_edge_cases(self):
        """Test risk band calculation edge cases"""
        # Test exact boundaries
        assert self.decision_core._get_risk_band(0.0) == "low"
        assert self.decision_core._get_risk_band(0.299) == "low"
        assert self.decision_core._get_risk_band(0.3) == "med"
        assert self.decision_core._get_risk_band(0.599) == "med"
        assert self.decision_core._get_risk_band(0.6) == "high"
        assert self.decision_core._get_risk_band(0.799) == "high"
        assert self.decision_core._get_risk_band(0.8) == "critical"
        assert self.decision_core._get_risk_band(1.0) == "critical"

    def test_matrix_key_generation(self):
        """Test matrix key generation"""
        key = self.decision_core._get_matrix_key("payment", "high", "premium")
        assert key == "payment:high:premium"

        key = self.decision_core._get_matrix_key("login", "low", "new")
        assert key == "login:low:new"
