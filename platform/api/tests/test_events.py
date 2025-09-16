"""
Unit tests for events API
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock

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
async def test_create_event_success(client, setup_database):
    """Test successful event creation"""
    event_data = {
        "event_type": "checkout",
        "event_data": {"amount": 100.0, "currency": "USD"},
        "profile_id": "user_123",
        "session_id": "session_456",
        "device_fingerprint": "device_789"
    }
    
    response = client.post(
        "/v1/events/?project_id=test-project-123",
        json=event_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == "checkout"
    assert data["profile_id"] == "user_123"
    assert data["session_id"] == "session_456"
    assert data["device_fingerprint"] == "device_789"
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_create_event_invalid_type(client, setup_database):
    """Test event creation with invalid event type"""
    event_data = {
        "event_type": "invalid_type",
        "event_data": {"amount": 100.0}
    }
    
    response = client.post(
        "/v1/events/?project_id=test-project-123",
        json=event_data
    )
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_event_missing_project(client, setup_database):
    """Test event creation without project ID"""
    event_data = {
        "event_type": "checkout",
        "event_data": {"amount": 100.0}
    }
    
    response = client.post("/v1/events/", json=event_data)
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_list_events(client, setup_database):
    """Test listing events"""
    # Create test events
    events = [
        {
            "event_type": "checkout",
            "event_data": {"amount": 100.0},
            "profile_id": "user_1"
        },
        {
            "event_type": "login",
            "event_data": {"ip": "192.168.1.1"},
            "profile_id": "user_2"
        }
    ]
    
    for event in events:
        client.post(
            "/v1/events/?project_id=test-project-123",
            json=event
        )
    
    response = client.get("/v1/events/?project_id=test-project-123")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 100

@pytest.mark.asyncio
async def test_list_events_with_filter(client, setup_database):
    """Test listing events with event type filter"""
    # Create test events
    events = [
        {"event_type": "checkout", "event_data": {"amount": 100.0}},
        {"event_type": "login", "event_data": {"ip": "192.168.1.1"}},
        {"event_type": "checkout", "event_data": {"amount": 200.0}}
    ]
    
    for event in events:
        client.post(
            "/v1/events/?project_id=test-project-123",
            json=event
        )
    
    response = client.get(
        "/v1/events/?project_id=test-project-123&event_type=checkout"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["events"]) == 2
    assert all(event["event_type"] == "checkout" for event in data["events"])

@pytest.mark.asyncio
async def test_get_event_by_id(client, setup_database):
    """Test getting a specific event by ID"""
    event_data = {
        "event_type": "checkout",
        "event_data": {"amount": 100.0},
        "profile_id": "user_123"
    }
    
    create_response = client.post(
        "/v1/events/?project_id=test-project-123",
        json=event_data
    )
    event_id = create_response.json()["id"]
    
    response = client.get(f"/v1/events/{event_id}?project_id=test-project-123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event_id
    assert data["event_type"] == "checkout"
    assert data["profile_id"] == "user_123"

@pytest.mark.asyncio
async def test_get_event_not_found(client, setup_database):
    """Test getting a non-existent event"""
    response = client.get(
        "/v1/events/non-existent-id?project_id=test-project-123"
    )
    
    assert response.status_code == 404
