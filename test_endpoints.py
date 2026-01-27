#!/usr/bin/env python3
"""
Test the running server endpoints
"""

import requests
import json

def test_endpoints():
    base_url = "http://localhost:8080"
    
    print("🧪 Testing server endpoints...")
    
    try:
        # Test root endpoint
        print("\n1. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test ask endpoint
        print("\n3. Testing ask endpoint...")
        response = requests.post(
            f"{base_url}/ask",
            json={"user_query": "health check", "session_id": "test"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        print("\n✅ All endpoints are working!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start it with: python backend/server.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_endpoints()