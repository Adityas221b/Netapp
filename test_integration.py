#!/usr/bin/env python3
"""
Integration test for CloudFlux AI
Tests frontend-backend connectivity and all major features
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Root status: {response.status_code}")
    data = response.json()
    print(f"   Name: {data['name']}")
    print(f"   Version: {data['version']}")
    print(f"   Features: {len(data['features'])}")
    return response.status_code == 200

def test_register_login():
    """Test user registration and login"""
    print("\n🔍 Testing registration and login...")
    
    # Register user
    register_data = {
        "username": f"testuser_{datetime.now().timestamp()}",
        "email": "test@cloudflux.ai",
        "password": "TestPassword123!",
        "role": "admin"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"✅ Registration status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.json()}")
        return None
    
    # Login
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data
    )
    print(f"✅ Login status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"   Token type: {token_data['token_type']}")
        user_info = token_data.get('user_info') or token_data.get('user', {})
        print(f"   User: {user_info.get('username', 'N/A')}")
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_cloud_status(token):
    """Test cloud status endpoint"""
    print("\n🔍 Testing cloud status...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/cloud/status", headers=headers)
    print(f"✅ Cloud status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   AWS: {'✓' if data['aws']['available'] else '✗'}")
        print(f"   Azure: {'✓' if data['azure']['available'] else '✗'}")
        print(f"   GCP: {'✓' if data['gcp']['available'] else '✗'}")
    return response.status_code == 200

def test_placement_analysis(token):
    """Test placement analysis endpoint"""
    print("\n🔍 Testing placement analysis...")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_data = {
        "file_name": "test_document.pdf",
        "size_gb": 2.5,
        "access_count_7d": 150,
        "access_count_30d": 500,
        "current_provider": "aws",
        "current_tier": "standard"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/placement/analyze",
        json=test_data,
        headers=headers
    )
    print(f"✅ Placement analysis status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Recommended tier: {data.get('recommended_tier', 'N/A')}")
        print(f"   Recommended provider: {data.get('recommended_provider', 'N/A')}")
        print(f"   Classification: {data.get('classification', 'N/A')}")
    return response.status_code == 200

def test_ml_model_info(token):
    """Test ML model info endpoint"""
    print("\n🔍 Testing ML model info...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/ml/model-info", headers=headers)
    print(f"✅ ML model info status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Model status: {data.get('status', 'N/A')}")
        if data.get('metrics'):
            print(f"   Accuracy: {data['metrics'].get('accuracy', 'N/A')}")
            print(f"   R² Score: {data['metrics'].get('r2_score', 'N/A')}")
    return response.status_code == 200

def test_analytics_overview(token):
    """Test analytics overview endpoint"""
    print("\n🔍 Testing analytics overview...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/overview", headers=headers)
    print(f"✅ Analytics overview status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total files: {data.get('total_files', 0)}")
        print(f"   Total size: {data.get('total_size_gb', 0)} GB")
    return response.status_code == 200

def main():
    """Run all integration tests"""
    print("="*80)
    print("🚀 CloudFlux AI - Integration Test Suite")
    print("="*80)
    
    results = []
    
    # Test public endpoints
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    
    # Test authentication
    token = test_register_login()
    if not token:
        print("\n❌ Authentication failed. Cannot proceed with authenticated tests.")
        return False
    
    results.append(("Authentication", True))
    
    # Test authenticated endpoints
    results.append(("Cloud Status", test_cloud_status(token)))
    results.append(("Placement Analysis", test_placement_analysis(token)))
    results.append(("ML Model Info", test_ml_model_info(token)))
    results.append(("Analytics Overview", test_analytics_overview(token)))
    
    # Print summary
    print("\n" + "="*80)
    print("📊 Test Results Summary")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✨ All tests passed! Frontend-backend integration is working! ✨")
    else:
        print("⚠️ Some tests failed. Please check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        exit(1)
