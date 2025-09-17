#!/usr/bin/env python3
"""
API Endpoints Testing Script
Tests all major API endpoints for the Anti-Fraud Platform
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        print("🔍 Testing health check...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                data = await response.json()
                print(f"✅ Health check: {data['status']}")
                if 'database' in data:
                    print(f"   Database: {data['database']['status']}")
                return data
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {"error": str(e)}
    
    async def test_database_health(self) -> Dict[str, Any]:
        """Test database health endpoint"""
        print("🔍 Testing database health...")
        try:
            async with self.session.get(f"{self.base_url}/health/database") as response:
                data = await response.json()
                print(f"✅ Database health: {data['status']}")
                return data
        except Exception as e:
            print(f"❌ Database health failed: {e}")
            return {"error": str(e)}
    
    async def test_create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test event creation endpoint"""
        print(f"🔍 Testing event creation: {event_data['event_type']}...")
        try:
            async with self.session.post(
                f"{self.base_url}/v2/events/",
                json=event_data
            ) as response:
                data = await response.json()
                print(f"✅ Event created: {data['event_id']} - Decision: {data['decision']} (Risk: {data['risk_score']:.3f})")
                return data
        except Exception as e:
            print(f"❌ Event creation failed: {e}")
            return {"error": str(e)}
    
    async def test_list_events(self, project_id: str = "550e8400-e29b-41d4-a716-446655440001") -> Dict[str, Any]:
        """Test event listing endpoint"""
        print("🔍 Testing event listing...")
        try:
            async with self.session.get(
                f"{self.base_url}/v2/events/",
                params={"project_id": project_id, "limit": 10}
            ) as response:
                data = await response.json()
                print(f"✅ Events listed: {data['total']} total events")
                return data
        except Exception as e:
            print(f"❌ Event listing failed: {e}")
            return {"error": str(e)}
    
    async def test_event_stats(self, project_id: str = "550e8400-e29b-41d4-a716-446655440001") -> Dict[str, Any]:
        """Test event statistics endpoint"""
        print("🔍 Testing event statistics...")
        try:
            async with self.session.get(
                f"{self.base_url}/v2/events/stats/summary",
                params={"project_id": project_id, "hours": 24}
            ) as response:
                data = await response.json()
                print(f"✅ Event stats: {data['total_events']} events, {data['avg_risk_score']:.3f} avg risk")
                return data
        except Exception as e:
            print(f"❌ Event stats failed: {e}")
            return {"error": str(e)}
    
    async def test_dashboard_stats(self, project_id: str = "550e8400-e29b-41d4-a716-446655440001") -> Dict[str, Any]:
        """Test dashboard statistics endpoint"""
        print("🔍 Testing dashboard statistics...")
        try:
            async with self.session.get(
                f"{self.base_url}/v1/dashboard/stats",
                params={"project_id": project_id, "hours": 24}
            ) as response:
                data = await response.json()
                print(f"✅ Dashboard stats: {data['total_events']} events, {data['allowed_events']} allowed, {data['denied_events']} denied")
                return data
        except Exception as e:
            print(f"❌ Dashboard stats failed: {e}")
            return {"error": str(e)}
    
    async def test_replay_worker(self) -> Dict[str, Any]:
        """Test replay worker endpoints"""
        print("🔍 Testing replay worker...")
        try:
            # Test worker status
            async with self.session.get(f"{self.base_url}/v1/replay/worker/status") as response:
                data = await response.json()
                print(f"✅ Replay worker status: {data}")
            
            # Test enqueue replay
            replay_data = {
                "event_ids": ["evt_1", "evt_2"],
                "schema_version": 1,
                "reason": "rule_change:rule_42@v7"
            }
            async with self.session.post(
                f"{self.base_url}/v1/replay/enqueue",
                json=replay_data
            ) as response:
                data = await response.json()
                print(f"✅ Replay job enqueued: {data['job_id']}")
            
            return data
        except Exception as e:
            print(f"❌ Replay worker test failed: {e}")
            return {"error": str(e)}
    
    async def run_comprehensive_test(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 50)
        
        # Test basic health
        await self.test_health_check()
        await self.test_database_health()
        
        print("\n" + "=" * 50)
        print("📊 Testing Event Processing Pipeline")
        print("=" * 50)
        
        # Test different event types
        test_events = [
            {
                "event_type": "login",
                "event_data": {"user_id": "user_123", "email": "test@example.com"},
                "profile_id": "user_123",
                "session_id": "session_456",
                "device_fingerprint": "device_hash_789",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            {
                "event_type": "payment",
                "event_data": {"order_id": "order_123", "payment_method": "credit_card"},
                "profile_id": "user_123",
                "amount": 99.99,
                "currency": "USD",
                "device_fingerprint": "device_hash_789",
                "ip_address": "203.0.113.1"
            },
            {
                "event_type": "signup",
                "event_data": {"email": "newuser@example.com", "source": "web"},
                "profile_id": "user_456",
                "device_fingerprint": "device_hash_abc",
                "ip_address": "198.51.100.1"
            },
            {
                "event_type": "checkout",
                "event_data": {"cart_id": "cart_789", "items": 3},
                "profile_id": "user_123",
                "amount": 149.99,
                "currency": "USD",
                "device_fingerprint": "device_hash_789"
            }
        ]
        
        # Process test events
        for i, event in enumerate(test_events, 1):
            print(f"\n--- Test Event {i} ---")
            await self.test_create_event(event)
            await asyncio.sleep(0.1)  # Small delay between events
        
        print("\n" + "=" * 50)
        print("📈 Testing Analytics and Monitoring")
        print("=" * 50)
        
        # Test analytics endpoints
        await self.test_list_events()
        await self.test_event_stats()
        await self.test_dashboard_stats()
        
        print("\n" + "=" * 50)
        print("🔄 Testing Replay Worker")
        print("=" * 50)
        
        # Test replay worker
        await self.test_replay_worker()
        
        print("\n" + "=" * 50)
        print("✅ Comprehensive API Test Suite Completed!")
        print("=" * 50)

async def main():
    """Main test function"""
    print("Anti-Fraud Platform API Test Suite")
    print("==================================")
    print(f"Testing against: http://localhost:8000")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    async with APITester() as tester:
        await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
