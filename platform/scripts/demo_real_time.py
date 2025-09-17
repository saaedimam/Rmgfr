#!/usr/bin/env python3
"""
Real-time Fraud Detection Demo
Demonstrates the real-time fraud detection capabilities
"""

import asyncio
import aiohttp
import json
import random
from datetime import datetime
from typing import List, Dict, Any

class FraudDetectionDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Send event to the API"""
        try:
            async with self.session.post(
                f"{self.base_url}/v2/events/",
                json=event
            ) as response:
                data = await response.json()
                return data
        except Exception as e:
            print(f"❌ Error sending event: {e}")
            return {"error": str(e)}
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            async with self.session.get(
                f"{self.base_url}/v1/dashboard/stats",
                params={"project_id": "550e8400-e29b-41d4-a716-446655440001", "hours": 1}
            ) as response:
                return await response.json()
        except Exception as e:
            print(f"❌ Error getting dashboard stats: {e}")
            return {"error": str(e)}
    
    def generate_test_events(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate test events with varying risk levels"""
        events = []
        
        # Low risk events
        low_risk_events = [
            {
                "event_type": "login",
                "event_data": {"user_id": f"user_{i}", "email": f"user{i}@example.com"},
                "profile_id": f"user_{i}",
                "session_id": f"session_{i}",
                "device_fingerprint": f"device_{i}_normal",
                "ip_address": f"192.168.1.{i % 254 + 1}",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            for i in range(count // 3)
        ]
        
        # Medium risk events
        medium_risk_events = [
            {
                "event_type": "payment",
                "event_data": {"order_id": f"order_{i}", "payment_method": "credit_card"},
                "profile_id": f"user_{i}",
                "amount": random.uniform(50, 500),
                "currency": "USD",
                "device_fingerprint": f"device_{i}_mobile",
                "ip_address": f"203.0.113.{i % 254 + 1}"
            }
            for i in range(count // 3, 2 * count // 3)
        ]
        
        # High risk events
        high_risk_events = [
            {
                "event_type": "signup",
                "event_data": {"email": f"test{i}@fake.com", "source": "web"},
                "profile_id": f"new_user_{i}",
                "device_fingerprint": f"device_{i}_suspicious",
                "ip_address": f"10.0.0.{i % 254 + 1}",
                "user_agent": "Bot/1.0 (Automated Test)"
            }
            for i in range(2 * count // 3, count)
        ]
        
        events.extend(low_risk_events)
        events.extend(medium_risk_events)
        events.extend(high_risk_events)
        
        # Shuffle events
        random.shuffle(events)
        
        return events
    
    async def run_demo(self):
        """Run the real-time fraud detection demo"""
        print("🎯 Real-time Fraud Detection Demo")
        print("=" * 40)
        print(f"Time: {datetime.now().isoformat()}")
        print()
        
        # Generate test events
        print("📝 Generating test events...")
        events = self.generate_test_events(15)
        print(f"✅ Generated {len(events)} test events")
        
        # Process events in real-time
        print("\n🔄 Processing events in real-time...")
        print("-" * 40)
        
        results = []
        for i, event in enumerate(events, 1):
            print(f"Event {i:2d}: {event['event_type']:8s} | ", end="")
            
            # Send event
            result = await self.send_event(event)
            
            if "error" not in result:
                decision = result.get("decision", "unknown")
                risk_score = result.get("risk_score", 0.0)
                processing_time = result.get("processing_time_ms", 0.0)
                
                # Color code the decision
                if decision == "allow":
                    decision_color = "🟢"
                elif decision == "deny":
                    decision_color = "🔴"
                elif decision == "review":
                    decision_color = "🟡"
                else:
                    decision_color = "⚪"
                
                print(f"{decision_color} {decision:6s} | Risk: {risk_score:.3f} | Time: {processing_time:.1f}ms")
                results.append(result)
            else:
                print(f"❌ Error: {result['error']}")
            
            # Small delay to simulate real-time processing
            await asyncio.sleep(0.2)
        
        # Show summary
        print("\n" + "=" * 40)
        print("📊 Processing Summary")
        print("=" * 40)
        
        if results:
            decisions = [r.get("decision", "unknown") for r in results]
            risk_scores = [r.get("risk_score", 0.0) for r in results]
            processing_times = [r.get("processing_time_ms", 0.0) for r in results]
            
            print(f"Total Events: {len(results)}")
            print(f"Allowed: {decisions.count('allow')}")
            print(f"Denied: {decisions.count('deny')}")
            print(f"Review: {decisions.count('review')}")
            print(f"Average Risk Score: {sum(risk_scores) / len(risk_scores):.3f}")
            print(f"Average Processing Time: {sum(processing_times) / len(processing_times):.1f}ms")
            print(f"Max Risk Score: {max(risk_scores):.3f}")
            print(f"Min Risk Score: {min(risk_scores):.3f}")
        
        # Get dashboard stats
        print("\n📈 Dashboard Statistics")
        print("-" * 40)
        
        stats = await self.get_dashboard_stats()
        if "error" not in stats:
            print(f"Total Events (1h): {stats.get('total_events', 0)}")
            print(f"Allowed Events: {stats.get('allowed_events', 0)}")
            print(f"Denied Events: {stats.get('denied_events', 0)}")
            print(f"Review Events: {stats.get('review_events', 0)}")
            print(f"Average Risk Score: {stats.get('avg_risk_score', 0.0):.3f}")
        else:
            print(f"❌ Error getting dashboard stats: {stats['error']}")
        
        print("\n✅ Demo completed!")

async def main():
    """Main demo function"""
    print("Anti-Fraud Platform - Real-time Demo")
    print("====================================")
    print("This demo shows real-time fraud detection capabilities")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    async with FraudDetectionDemo() as demo:
        await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
