"""
Unit tests for decisions API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.models.database import Base, get_db

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_create_decision_success(client, setup_database):
    """Test successful decision creation"""
    decision_data = {
        "decision": "allow",
        "risk_score": 0.2,
        "reasons": ["Low risk profile", "Normal transaction pattern"],
        "rules_fired": ["velocity_check"],
        "metadata": {"confidence": 0.95}
    }
    
    response = client.post(
        "/v1/decisions/?project_id=test-project-123",
        json=decision_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["decision"] == "allow"
    assert data["risk_score"] == 0.2
    assert data["reasons"] == ["Low risk profile", "Normal transaction pattern"]
    assert data["rules_fired"] == ["velocity_check"]
    assert data["metadata"]["confidence"] == 0.95
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_create_decision_invalid_decision(client, setup_database):
    """Test decision creation with invalid decision value"""
    decision_data = {
        "decision": "invalid_decision",
        "risk_score": 0.2,
        "reasons": ["Test reason"]
    }
    
    response = client.post(
        "/v1/decisions/?project_id=test-project-123",
        json=decision_data
    )
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_decision_invalid_risk_score(client, setup_database):
    """Test decision creation with invalid risk score"""
    decision_data = {
        "decision": "allow",
        "risk_score": 1.5,  # Invalid: should be 0-1
        "reasons": ["Test reason"]
    }
    
    response = client.post(
        "/v1/decisions/?project_id=test-project-123",
        json=decision_data
    )
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_list_decisions(client, setup_database):
    """Test listing decisions"""
    # Create test decisions
    decisions = [
        {
            "decision": "allow",
            "risk_score": 0.2,
            "reasons": ["Low risk"]
        },
        {
            "decision": "deny",
            "risk_score": 0.9,
            "reasons": ["High risk"]
        },
        {
            "decision": "review",
            "risk_score": 0.6,
            "reasons": ["Medium risk"]
        }
    ]
    
    for decision in decisions:
        client.post(
            "/v1/decisions/?project_id=test-project-123",
            json=decision
        )
    
    response = client.get("/v1/decisions/?project_id=test-project-123")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["decisions"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["limit"] == 100

@pytest.mark.asyncio
async def test_list_decisions_with_filter(client, setup_database):
    """Test listing decisions with decision filter"""
    # Create test decisions
    decisions = [
        {"decision": "allow", "risk_score": 0.2, "reasons": ["Low risk"]},
        {"decision": "deny", "risk_score": 0.9, "reasons": ["High risk"]},
        {"decision": "allow", "risk_score": 0.3, "reasons": ["Low risk"]}
    ]
    
    for decision in decisions:
        client.post(
            "/v1/decisions/?project_id=test-project-123",
            json=decision
        )
    
    response = client.get(
        "/v1/decisions/?project_id=test-project-123&decision=allow"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["decisions"]) == 2
    assert all(decision["decision"] == "allow" for decision in data["decisions"])

@pytest.mark.asyncio
async def test_get_decision_by_id(client, setup_database):
    """Test getting a specific decision by ID"""
    decision_data = {
        "decision": "allow",
        "risk_score": 0.2,
        "reasons": ["Low risk profile"]
    }
    
    create_response = client.post(
        "/v1/decisions/?project_id=test-project-123",
        json=decision_data
    )
    decision_id = create_response.json()["id"]
    
    response = client.get(f"/v1/decisions/{decision_id}?project_id=test-project-123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == decision_id
    assert data["decision"] == "allow"
    assert data["risk_score"] == 0.2

@pytest.mark.asyncio
async def test_get_decision_not_found(client, setup_database):
    """Test getting a non-existent decision"""
    response = client.get(
        "/v1/decisions/non-existent-id?project_id=test-project-123"
    )
    
    assert response.status_code == 404
