#!/usr/bin/env python3
"""
Quick test script for Salesforce Case Assistant API
Run this to validate your deployment is working correctly.
"""

import requests
import json
import sys
from typing import Dict, Any

def test_api(base_url: str = "http://localhost:8080") -> None:
    """Test the Salesforce Case Assistant API endpoints"""
    
    print(f"🧪 Testing Salesforce Case Assistant API at: {base_url}")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. 🏥 Testing Salesforce Health Check...")
    try:
        response = requests.get(f"{base_url}/health/salesforce", timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Response: {json.dumps(health_data, indent=2)}")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Basic Case Query
    print("\n2. 📋 Testing Basic Case Query...")
    test_query = {
        "query": "Check Salesforce connection",
        "session_id": "quick-test"
    }
    
    try:
        response = requests.post(
            f"{base_url}/query",
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            query_data = response.json()
            print(f"   Response Type: {query_data.get('type', 'unknown')}")
            print(f"   Message: {query_data.get('message', 'No message')}")
            print("   ✅ Query endpoint working")
        else:
            print(f"   ❌ Query failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Query error: {e}")
    
    # Test 3: Case Number Query
    print("\n3. 🔍 Testing Case Number Query...")
    case_query = {
        "query": "Show me case 12345",
        "session_id": "quick-test"
    }
    
    try:
        response = requests.post(
            f"{base_url}/query",
            json=case_query,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            case_data = response.json()
            print(f"   Response Type: {case_data.get('type', 'unknown')}")
            if case_data.get('type') == 'case_data':
                print("   ✅ Case lookup working")
            elif case_data.get('type') == 'clarification':
                print("   ℹ️  Case not found (expected if case 12345 doesn't exist)")
            else:
                print(f"   ⚠️  Unexpected response type: {case_data.get('type')}")
        else:
            print(f"   ❌ Case query failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Case query error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("   - If health check passes: Salesforce connection is working")
    print("   - If query endpoint works: API is functional") 
    print("   - If case lookup works: Full functionality available")
    print("\n💡 Next steps:")
    print("   - Test with real case numbers from your Salesforce org")
    print("   - Try other queries like 'List all in progress cases'")
    print("   - Set up Custom GPT using custom-gpt-schema.json")

def main():
    """Main function to run tests"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = input("Enter API base URL (or press Enter for http://localhost:8080): ").strip()
        if not base_url:
            base_url = "http://localhost:8080"
    
    test_api(base_url)

if __name__ == "__main__":
    main()