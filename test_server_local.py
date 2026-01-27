#!/usr/bin/env python3
"""
Test the server locally before deploying
"""

import requests
import time
import subprocess
import sys
import os

def test_local_server():
    print("🧪 Testing local server...")
    
    # Start server
    print("Starting server...")
    process = subprocess.Popen(
        [sys.executable, "backend/server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8080/health", timeout=10)
        print(f"Health check status: {response.status_code}")
        print(f"Health response: {response.json()}")
        
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get("http://localhost:8080/", timeout=10)
        print(f"Root status: {response.status_code}")
        print(f"Root response: {response.json()}")
        
        # Test ask endpoint
        print("Testing ask endpoint...")
        response = requests.post(
            "http://localhost:8080/ask",
            json={"user_query": "health check", "session_id": "test"},
            timeout=30
        )
        print(f"Ask status: {response.status_code}")
        print(f"Ask response: {response.json()}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Stop server
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_local_server()