"""
Unit tests for fraud detection engine
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.services.fraud_engine import FraudEngine
from src.models.database import Base, Event, Profile, Rule

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="function")
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(setup_database):
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def fraud_engine(db_session):
    return FraudEngine(db_session)

@pytest.mark.asyncio
async def test_evaluate_rate_limit_rule(fraud_engine, db_session):
    """Test rate limiting rule evaluation"""
    # Create test event
    event = Event(
        id="test-event-1",
        project_id="test-project",
        event_type="checkout",
        event_data={"amount": 100.0},
        ip_address="192.168.1.1",
        created_at=datetime.utcnow()
    )
    
    # Create rate limit rule
    rule = Rule(
        id="test-rule-1",
        project_id="test-project",
        name="IP Rate Limit",
        rule_type="rate_limit",
        conditions={
            "scope": "ip",
            "time_window_minutes": 60,
            "max_events": 5
        },
        action="deny",
        priority=1,
        enabled=True
    )
    
    # Mock database query for event count
    mock_result = MagicMock()
    mock_result.scalar.return_value = 6  # Exceeds limit
    db_session.execute = AsyncMock(return_value=mock_result)
    
    result = await fraud_engine._evaluate_rate_limit_rule(rule, event, None)
    
    assert result["fired"] is True
    assert "Rate limit exceeded" in result["reason"]
    assert result["risk_score"] > 0

@pytest.mark.asyncio
async def test_evaluate_velocity_rule(fraud_engine, db_session):
    """Test velocity rule evaluation"""
    # Create test event and profile
    profile = Profile(
        id="test-profile-1",
        project_id="test-project",
        external_id="user_123"
    )
    
    event = Event(
        id="test-event-1",
        project_id="test-project",
        profile_id="test-profile-1",
        event_type="checkout",
        event_data={"amount": 100.0},
        created_at=datetime.utcnow()
    )
    
    # Create velocity rule
    rule = Rule(
        id="test-rule-1",
        project_id="test-project",
        name="User Velocity",
        rule_type="velocity",
        conditions={
            "scope": "profile",
            "time_window_minutes": 60,
            "max_velocity": 10
        },
        action="review",
        priority=2,
        enabled=True
    )
    
    # Mock database query for event count
    mock_result = MagicMock()
    mock_result.scalar.return_value = 12  # Exceeds velocity
    db_session.execute = AsyncMock(return_value=mock_result)
    
    result = await fraud_engine._evaluate_velocity_rule(rule, event, profile)
    
    assert result["fired"] is True
    assert "Velocity exceeded" in result["reason"]
    assert result["risk_score"] > 0

@pytest.mark.asyncio
async def test_evaluate_device_rule(fraud_engine, db_session):
    """Test device fingerprinting rule evaluation"""
    # Create test event
    event = Event(
        id="test-event-1",
        project_id="test-project",
        event_type="checkout",
        event_data={"amount": 100.0},
        device_fingerprint="device_123",
        created_at=datetime.utcnow()
    )
    
    # Create device rule
    rule = Rule(
        id="test-rule-1",
        project_id="test-project",
        name="Device Overuse",
        rule_type="device",
        conditions={
            "check_device_reuse": True,
            "max_device_uses": 5
        },
        action="deny",
        priority=3,
        enabled=True
    )
    
    # Mock database query for device count
    mock_result = MagicMock()
    mock_result.scalar.return_value = 8  # Exceeds device uses
    db_session.execute = AsyncMock(return_value=mock_result)
    
    result = await fraud_engine._evaluate_device_rule(rule, event, None)
    
    assert result["fired"] is True
    assert "Device overuse" in result["reason"]
    assert result["risk_score"] > 0

@pytest.mark.asyncio
async def test_evaluate_custom_rule(fraud_engine, db_session):
    """Test custom rule evaluation"""
    # Create test event
    event = Event(
        id="test-event-1",
        project_id="test-project",
        event_type="checkout",
        event_data={"description": "suspicious transaction", "amount": 100.0},
        created_at=datetime.utcnow()
    )
    
    # Create custom rule
    rule = Rule(
        id="test-rule-1",
        project_id="test-project",
        name="Suspicious Keywords",
        rule_type="custom",
        conditions={
            "check_event_data": True,
            "suspicious_keywords": ["suspicious", "fraud", "scam"]
        },
        action="review",
        priority=4,
        enabled=True
    )
    
    result = await fraud_engine._evaluate_custom_rule(rule, event, None)
    
    assert result["fired"] is True
    assert "Suspicious keyword detected" in result["reason"]
    assert result["risk_score"] == 0.6

@pytest.mark.asyncio
async def test_evaluate_event_comprehensive(fraud_engine, db_session):
    """Test comprehensive event evaluation with multiple rules"""
    # Create test event and profile
    profile = Profile(
        id="test-profile-1",
        project_id="test-project",
        external_id="user_123"
    )
    
    event = Event(
        id="test-event-1",
        project_id="test-project",
        profile_id="test-profile-1",
        event_type="checkout",
        event_data={"amount": 100.0},
        ip_address="192.168.1.1",
        device_fingerprint="device_123",
        created_at=datetime.utcnow()
    )
    
    # Create multiple rules
    rules = [
        Rule(
            id="rule-1",
            project_id="test-project",
            name="IP Rate Limit",
            rule_type="rate_limit",
            conditions={"scope": "ip", "time_window_minutes": 60, "max_events": 5},
            action="deny",
            priority=1,
            enabled=True
        ),
        Rule(
            id="rule-2",
            project_id="test-project",
            name="User Velocity",
            rule_type="velocity",
            conditions={"scope": "profile", "time_window_minutes": 60, "max_velocity": 10},
            action="review",
            priority=2,
            enabled=True
        )
    ]
    
    # Mock database queries
    mock_result = MagicMock()
    mock_result.scalar.return_value = 3  # Within limits
    db_session.execute = AsyncMock(return_value=mock_result)
    
    # Mock rules query
    mock_rules_result = MagicMock()
    mock_rules_result.scalars.return_value.all.return_value = rules
    db_session.execute = AsyncMock(return_value=mock_rules_result)
    
    result = await fraud_engine.evaluate_event("test-event-1", "test-project")
    
    assert result["decision"] == "allow"  # No rules fired
    assert result["risk_score"] == 0.0
    assert len(result["reasons"]) == 2  # Both rules evaluated
    assert len(result["rules_fired"]) == 0
