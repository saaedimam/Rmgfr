#!/usr/bin/env python3
"""
Anti-Fraud Platform Startup Script
Starts all services and runs comprehensive tests
"""

import subprocess
import time
import asyncio
import aiohttp
import sys
from pathlib import Path
from typing import List, Dict, Any

class PlatformManager:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.base_url = "http://localhost:8000"
        self.web_url = "http://localhost:3000"
    
    def start_api_server(self):
        """Start the FastAPI server"""
        print("🚀 Starting API server...")
        
        api_dir = Path(__file__).parent.parent / "api"
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.main:app", "--reload", "--port", "8000"],
            cwd=api_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes.append(process)
        print(f"✅ API server started with PID: {process.pid}")
        return process
    
    def start_web_server(self):
        """Start the Next.js web server"""
        print("🌐 Starting web server...")
        
        web_dir = Path(__file__).parent.parent / "web"
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=web_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes.append(process)
        print(f"✅ Web server started with PID: {process.pid}")
        return process
    
    async def wait_for_service(self, url: str, name: str, max_wait: int = 30):
        """Wait for a service to be ready"""
        print(f"⏳ Waiting for {name} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            print(f"✅ {name} is ready!")
                            return True
            except:
                pass
            
            time.sleep(1)
            print(".", end="", flush=True)
        
        print(f"\n❌ {name} not ready after {max_wait} seconds")
        return False
    
    async def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🧪 Testing API endpoints...")
        
        test_cases = [
            ("/health", "Health check"),
            ("/health/database", "Database health"),
            ("/v2/events/", "Event creation"),
            ("/v1/dashboard/stats", "Dashboard stats"),
            ("/v1/replay/worker/status", "Replay worker")
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint, description in test_cases:
                try:
                    url = f"{self.base_url}{endpoint}"
                    if endpoint == "/v2/events/":
                        # Test event creation
                        test_event = {
                            "event_type": "login",
                            "event_data": {"user_id": "test_user", "email": "test@example.com"},
                            "profile_id": "user_123",
                            "device_fingerprint": "device_hash_789",
                            "ip_address": "192.168.1.1"
                        }
                        async with session.post(url, json=test_event) as response:
                            if response.status in [200, 201]:
                                print(f"✅ {description}: {response.status}")
                            else:
                                print(f"❌ {description}: {response.status}")
                    else:
                        async with session.get(url) as response:
                            if response.status == 200:
                                print(f"✅ {description}: {response.status}")
                            else:
                                print(f"❌ {description}: {response.status}")
                except Exception as e:
                    print(f"❌ {description}: {e}")
    
    async def test_web_endpoints(self):
        """Test web endpoints"""
        print("\n🌐 Testing web endpoints...")
        
        test_cases = [
            ("/", "Home page"),
            ("/dashboard/fraud", "Fraud dashboard"),
            ("/dashboard/fraud/realtime", "Real-time monitoring"),
            ("/dashboard/fraud/test", "Event testing"),
            ("/dashboard/fraud/analytics", "Analytics"),
            ("/dashboard/fraud/settings", "Settings")
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint, description in test_cases:
                try:
                    url = f"{self.web_url}{endpoint}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            print(f"✅ {description}: {response.status}")
                        else:
                            print(f"❌ {description}: {response.status}")
                except Exception as e:
                    print(f"❌ {description}: {e}")
    
    async def run_demo_events(self):
        """Run demo events"""
        print("\n🎯 Running demo events...")
        
        demo_events = [
            {
                "event_type": "login",
                "event_data": {"user_id": "demo_user_1", "email": "demo1@example.com"},
                "profile_id": "user_1",
                "device_fingerprint": "device_demo_1",
                "ip_address": "192.168.1.1"
            },
            {
                "event_type": "payment",
                "event_data": {"order_id": "order_123", "payment_method": "credit_card"},
                "profile_id": "user_1",
                "amount": 99.99,
                "currency": "USD",
                "device_fingerprint": "device_demo_1",
                "ip_address": "203.0.113.1"
            },
            {
                "event_type": "signup",
                "event_data": {"email": "newuser@example.com", "source": "web"},
                "profile_id": "user_2",
                "device_fingerprint": "device_demo_2",
                "ip_address": "198.51.100.1"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, event in enumerate(demo_events, 1):
                try:
                    async with session.post(f"{self.base_url}/v2/events/", json=event) as response:
                        if response.status in [200, 201]:
                            data = await response.json()
                            print(f"✅ Event {i}: {event['event_type']} - {data.get('decision', 'unknown')} (Risk: {data.get('risk_score', 0):.3f})")
                        else:
                            print(f"❌ Event {i}: {event['event_type']} - HTTP {response.status}")
                except Exception as e:
                    print(f"❌ Event {i}: {e}")
                
                await asyncio.sleep(0.5)  # Small delay between events
    
    def cleanup(self):
        """Clean up all processes"""
        print("\n🧹 Cleaning up...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Process {process.pid} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  Process {process.pid} force killed")
            except Exception as e:
                print(f"❌ Error stopping process {process.pid}: {e}")
    
    async def run(self):
        """Run the complete platform"""
        print("🎯 Anti-Fraud Platform Startup")
        print("=" * 40)
        
        try:
            # Start services
            self.start_api_server()
            self.start_web_server()
            
            # Wait for services to be ready
            api_ready = await self.wait_for_service(f"{self.base_url}/health", "API Server")
            web_ready = await self.wait_for_service(f"{self.web_url}", "Web Server")
            
            if not api_ready or not web_ready:
                print("❌ Failed to start services")
                return 1
            
            # Run tests
            await self.test_api_endpoints()
            await self.test_web_endpoints()
            await self.run_demo_events()
            
            print("\n" + "=" * 40)
            print("✅ Platform is running successfully!")
            print("=" * 40)
            print(f"🌐 Web Dashboard: {self.web_url}")
            print(f"🔌 API Server: {self.base_url}")
            print(f"📊 API Docs: {self.base_url}/docs")
            print("\nPress Ctrl+C to stop all services")
            
            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
        
        finally:
            self.cleanup()

async def main():
    """Main function"""
    manager = PlatformManager()
    return await manager.run()

if __name__ == "__main__":
    exit(asyncio.run(main()))
