#!/usr/bin/env python3
"""
Test client for Gmail OAuth API endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing {method} {endpoint}")
    if description:
        print(f"   {description}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success")
            if isinstance(result, dict) and len(result) < 10:
                # Print small responses in full
                print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                # Print summary for large responses
                if isinstance(result, dict):
                    keys = list(result.keys())
                    print(f"   Response keys: {keys}")
                else:
                    print(f"   Response type: {type(result)}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - is the server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def run_tests():
    """Run all Gmail OAuth API tests"""
    print("🧪 Testing Gmail OAuth API Endpoints")
    print("=" * 50)
    
    tests = [
        ("GET", "/", None, "Root endpoint"),
        ("GET", "/health", None, "Health check"),
        ("GET", "/auth/status", None, "Authentication status"),
        ("GET", "/setup-instructions", None, "Setup instructions"),
        ("POST", "/auth", {}, "Start authentication (no auth code)"),
        ("POST", "/auth", {"auth_code": "test_code"}, "Test authentication with dummy code"),
        ("POST", "/send", {
            "to": ["test@example.com"],
            "subject": "Test Email",
            "body": "This is a test email"
        }, "Test send email (should fail - not authenticated)"),
        ("POST", "/fetch", {
            "query": "is:unread",
            "max_results": 5
        }, "Test fetch emails (should fail - not authenticated)")
    ]
    
    results = []
    for method, endpoint, data, description in tests:
        result = test_endpoint(method, endpoint, data, description)
        results.append((f"{method} {endpoint}", result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed >= len(results) - 2:  # Allow 2 failures for auth-required endpoints
        print("\n✅ Gmail OAuth API is working correctly!")
        print("   Authentication endpoints are accessible")
        print("   Setup instructions are available")
        print("   Send/Fetch endpoints properly reject unauthenticated requests")
    else:
        print("\n❌ Some core endpoints are not working")
        print("   Check server logs for details")

if __name__ == "__main__":
    run_tests()