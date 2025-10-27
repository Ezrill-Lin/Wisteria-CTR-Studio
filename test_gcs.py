#!/usr/bin/env python3
"""Test script for Google Cloud Storage integration.

This script tests the new GCS functionality including identity bank loading
and the new API endpoints.
"""

import os
import json
import requests
from typing import Dict, Any

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")


def test_identities_endpoint():
    """Test the /identities endpoint."""
    print("Testing /identities endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/identities")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Identity bank loaded from: {data.get('source', 'unknown')}")
            bank = data.get('identity_bank', {})
            print(f"   Categories available: {list(bank.keys())}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_reload_endpoint():
    """Test the /identities/reload endpoint."""
    print("\nTesting /identities/reload endpoint...")
    try:
        response = requests.post(f"{API_BASE_URL}/identities/reload")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Identity bank reloaded from: {data.get('source', 'unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_prediction_with_gcs():
    """Test CTR prediction to ensure GCS integration doesn't break existing functionality."""
    print("\nTesting CTR prediction with GCS integration...")
    try:
        payload = {
            "ad_text": "Test advertisement for cloud storage integration",
            "population_size": 10,
            "use_mock": True
        }
        
        response = requests.post(f"{API_BASE_URL}/predict-ctr", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CTR prediction successful: {data.get('ctr', 'N/A')}")
            print(f"   Total identities: {data.get('total_identities', 'N/A')}")
            print(f"   Provider used: {data.get('provider_used', 'N/A')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_health_check():
    """Test the health check endpoint."""
    print("\nTesting health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def main():
    """Run all tests."""
    print(f"🧪 Testing Wisteria CTR Studio API at {API_BASE_URL}")
    print("=" * 60)
    
    tests = [
        test_health_check,
        test_identities_endpoint,
        test_reload_endpoint,
        test_prediction_with_gcs,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GCS integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit(main())