"""
Test suite for Anti-Fraud Platform API
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "uptime" in data


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Anti-Fraud Platform API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"


class TestItemsEndpoints:
    """Test items CRUD endpoints"""
    
    def test_get_items_empty(self):
        """Test getting items when none exist"""
        response = client.get("/items")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_item(self):
        """Test creating a new item"""
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 29.99,
            "category": "test"
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] == item_data["description"]
        assert data["price"] == item_data["price"]
        assert data["category"] == item_data["category"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_item_validation(self):
        """Test item creation validation"""
        # Test missing required fields
        response = client.post("/items", json={})
        assert response.status_code == 422
        
        # Test invalid price
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": -10.0,
            "category": "test"
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 422
    
    def test_get_item_by_id(self):
        """Test getting item by ID"""
        # First create an item
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 29.99,
            "category": "test"
        }
        create_response = client.post("/items", json=item_data)
        item_id = create_response.json()["id"]
        
        # Then get it by ID
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == item_data["name"]
    
    def test_get_item_not_found(self):
        """Test getting non-existent item"""
        response = client.get("/items/999")
        assert response.status_code == 404
        data = response.json()
        assert "Item not found" in data["error"]
    
    def test_get_items_with_pagination(self):
        """Test getting items with pagination"""
        # Create multiple items
        for i in range(5):
            item_data = {
                "name": f"Test Item {i}",
                "description": f"A test item {i}",
                "price": 29.99 + i,
                "category": "test"
            }
            client.post("/items", json=item_data)
        
        # Test pagination
        response = client.get("/items?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error_format(self):
        """Test 404 error response format"""
        response = client.get("/items/999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "detail" in data
        assert "timestamp" in data

