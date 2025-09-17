#!/usr/bin/env python3
"""
Start API and Run Tests
Starts the API server and runs comprehensive tests
"""

import subprocess
import time
import asyncio
import sys
from pathlib import Path

def start_api_server():
    """Start the API server in background"""
    print("🚀 Starting API server...")

    # Change to API directory
    api_dir = Path(__file__).parent.parent / "api"

    # Start the server
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--reload", "--port", "8000"],
        cwd=api_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print(f"✅ API server started with PID: {process.pid}")
    return process

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to be ready...")

    import requests
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass

        time.sleep(1)
        print(".", end="", flush=True)

    print(f"\n❌ Server not ready after {max_wait} seconds")
    return False

def run_tests():
    """Run API tests"""
    print("\n🧪 Running API tests...")

    test_script = Path(__file__).parent / "test_api_endpoints.py"

    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            timeout=60
        )

        print("Test Output:")
        print(result.stdout)

        if result.stderr:
            print("Test Errors:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    """Main function"""
    print("Anti-Fraud Platform - API Test Runner")
    print("=====================================")

    # Start API server
    server_process = start_api_server()

    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("❌ Failed to start server")
            return 1

        # Run tests
        if run_tests():
            print("\n✅ All tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1

    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            print("✅ Server stopped")
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("⚠️  Server force killed")

if __name__ == "__main__":
    exit(main())
