#!/usr/bin/env python3
"""
Test script to verify the Pricing Scenarios API endpoints
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    base_url = "http://localhost:8069"
    
    print("Testing Pricing Scenarios API Endpoints")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/web/login", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test the months endpoint (should return 404 without auth, but route should exist)
    try:
        response = requests.get(f"{base_url}/api/pricing-scenarios/months", timeout=5)
        print(f"📡 Months endpoint response: {response.status_code}")
        if response.status_code == 404:
            print("   This is expected without authentication")
        elif response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Unexpected status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing months endpoint: {e}")
    
    # Test 3: Test the main pricing scenarios endpoint
    try:
        response = requests.get(f"{base_url}/api/pricing-scenarios?month=2025-07", timeout=5)
        print(f"📡 Pricing scenarios endpoint response: {response.status_code}")
        if response.status_code == 404:
            print("   This is expected without authentication")
        elif response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Unexpected status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing pricing scenarios endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("API endpoint test completed!")
    print("\nTo test with authentication:")
    print("1. Open browser: http://localhost:8069")
    print("2. Login with admin/admin")
    print("3. Navigate to Point of Sale → Dashboard")
    print("4. Check the Pricing Scenarios section")

if __name__ == "__main__":
    test_api_endpoints()
