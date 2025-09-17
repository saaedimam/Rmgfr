#!/usr/bin/env python3
"""
Test Database Service
Tests the database service without requiring a real database
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the API directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "api" / "src"))

from services.database import DatabaseService

async def test_database_service():
    """Test database service functionality"""
    print("Testing Database Service...")
    
    # Test 1: Service initialization without URL
    print("\n1. Testing initialization without database URL...")
    db_service = DatabaseService()
    db_service.db_url = None
    
    try:
        await db_service.initialize()
        print("❌ Should have failed without database URL")
    except ValueError as e:
        print(f"✅ Correctly failed without database URL: {e}")
    
    # Test 2: Health check without pool
    print("\n2. Testing health check without pool...")
    db_service = DatabaseService()
    health = await db_service.health_check()
    
    if health["status"] == "unhealthy":
        print("✅ Health check correctly reports unhealthy without pool")
    else:
        print(f"❌ Health check should report unhealthy: {health}")
    
    # Test 3: Operations without pool
    print("\n3. Testing operations without pool...")
    db_service = DatabaseService()
    
    try:
        await db_service.execute_query("SELECT 1")
        print("❌ Should have failed without pool")
    except RuntimeError as e:
        print(f"✅ Correctly failed without pool: {e}")
    
    try:
        await db_service.execute_one("SELECT 1")
        print("❌ Should have failed without pool")
    except RuntimeError as e:
        print(f"✅ Correctly failed without pool: {e}")
    
    try:
        await db_service.execute_command("SELECT 1")
        print("❌ Should have failed without pool")
    except RuntimeError as e:
        print(f"✅ Correctly failed without pool: {e}")
    
    # Test 4: Close without pool
    print("\n4. Testing close without pool...")
    db_service = DatabaseService()
    await db_service.close()
    print("✅ Close without pool works correctly")
    
    print("\n🎉 All database service tests passed!")
    return True

async def main():
    """Main test function"""
    try:
        success = await test_database_service()
        return success
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
