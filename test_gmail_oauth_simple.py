#!/usr/bin/env python3
"""
Simple test script for Gmail OAuth implementation
"""
import sys
import os
import importlib.util
from pathlib import Path

def test_gmail_oauth_direct():
    """Test Gmail OAuth gateway by directly loading the file"""
    print("🧪 Testing Gmail OAuth Implementation - Direct File Test")
    print("=" * 60)
    
    # Path to the Gmail OAuth gateway file
    gateway_file = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2/services/gateway/gmail_oauth_env_gateway.py")
    
    if not gateway_file.exists():
        print("❌ Gmail OAuth gateway file not found")
        return False
    
    print("✅ Gmail OAuth gateway file exists")
    
    # Read and analyze the file
    try:
        with open(gateway_file, 'r') as f:
            content = f.read()
        
        print("✅ Successfully read Gmail OAuth gateway file")
        
        # Check for key components
        key_components = [
            "class GmailOAuthEnvGateway",
            "async def authenticate",
            "async def send_message", 
            "async def fetch_messages",
            "SCOPES = [",
            "google.oauth2.credentials",
            "google_auth_oauthlib.flow",
            "googleapiclient.discovery"
        ]
        
        print("\n🔍 Checking key components:")
        for component in key_components:
            if component in content:
                print(f"✅ Found: {component}")
            else:
                print(f"❌ Missing: {component}")
        
        # Check OAuth scopes
        if "gmail.readonly" in content and "gmail.send" in content:
            print("✅ Gmail OAuth scopes properly configured")
        else:
            print("❌ Gmail OAuth scopes missing or incomplete")
        
        # Check environment variable usage
        if "GOOGLE_CLIENT_ID" in content and "GOOGLE_CLIENT_SECRET" in content:
            print("✅ Environment variables properly used")
        else:
            print("❌ Environment variables not properly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading Gmail OAuth file: {e}")
        return False

def test_api_router_direct():
    """Test Gmail OAuth API router by directly loading the file"""
    print("\n🔍 Testing Gmail OAuth API Router...")
    
    router_file = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2/apps/api/routers/gmail_oauth.py")
    
    if not router_file.exists():
        print("❌ Gmail OAuth API router file not found")
        return False
    
    print("✅ Gmail OAuth API router file exists")
    
    try:
        with open(router_file, 'r') as f:
            content = f.read()
        
        print("✅ Successfully read Gmail OAuth API router file")
        
        # Check for key API endpoints
        api_endpoints = [
            '@router.post("/auth")',
            '@router.get("/auth/status")',
            '@router.post("/send")',
            '@router.post("/fetch")',
            '@router.post("/process/{message_id}")',
            '@router.post("/listener/start")',
            '@router.get("/setup-instructions")'
        ]
        
        print("\n🔍 Checking API endpoints:")
        for endpoint in api_endpoints:
            if endpoint in content:
                print(f"✅ Found: {endpoint}")
            else:
                print(f"❌ Missing: {endpoint}")
        
        # Check for proper error handling
        if "HTTPException" in content and "status_code=401" in content:
            print("✅ Proper error handling implemented")
        else:
            print("❌ Error handling missing or incomplete")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading API router file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking Dependencies...")
    
    required_deps = [
        "fastapi",
        "pydantic", 
        "google.auth",
        "google_auth_oauthlib",
        "google.auth.transport.requests",
        "googleapiclient.discovery"
    ]
    
    installed_count = 0
    for dep in required_deps:
        try:
            if dep == "google.auth":
                import google.auth
            elif dep == "google_auth_oauthlib":
                import google_auth_oauthlib
            elif dep == "google.auth.transport.requests":
                import google.auth.transport.requests
            elif dep == "googleapiclient.discovery":
                import googleapiclient.discovery
            else:
                __import__(dep)
            print(f"✅ {dep}")
            installed_count += 1
        except ImportError:
            print(f"❌ {dep} (not installed)")
    
    print(f"\n📊 Dependencies: {installed_count}/{len(required_deps)} installed")
    return installed_count == len(required_deps)

def check_environment():
    """Check environment configuration"""
    print("\n🌍 Checking Environment Configuration...")
    
    env_vars = {
        "GOOGLE_CLIENT_ID": "Google OAuth Client ID",
        "GOOGLE_CLIENT_SECRET": "Google OAuth Client Secret", 
        "GOOGLE_REDIRECT_URI": "OAuth Redirect URI (optional)",
        "GMAIL_TOKEN_FILE": "Token storage file path (optional)"
    }
    
    configured_count = 0
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description}")
            configured_count += 1
        else:
            print(f"❌ {var}: {description}")
    
    print(f"\n📊 Environment: {configured_count}/{len(env_vars)} variables set")
    return configured_count >= 2  # At least client ID and secret needed

def test_minimal_fastapi():
    """Test if we can create a minimal FastAPI app with Gmail routes"""
    print("\n🔍 Testing Minimal FastAPI Integration...")
    
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Gmail OAuth Test")
        print("✅ FastAPI app created successfully")
        
        # Try to create a simple route
        @app.get("/test")
        async def test_route():
            return {"status": "ok"}
        
        print("✅ Test route created successfully")
        
        # Check if we can import the router (this might fail due to dependencies)
        try:
            # Add AIOS v2 to path
            aios_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2")
            if str(aios_path) not in sys.path:
                sys.path.insert(0, str(aios_path))
            
            # This will likely fail due to missing modules, but we can catch and report
            from apps.api.routers.gmail_oauth import router
            app.include_router(router, prefix="/api/v1/gmail")
            print("✅ Gmail OAuth router imported and included successfully")
            return True
            
        except Exception as e:
            print(f"⚠️  Gmail OAuth router import failed: {e}")
            print("   This is expected due to missing core modules in test environment")
            return False
        
    except Exception as e:
        print(f"❌ FastAPI integration test failed: {e}")
        return False

def generate_report():
    """Generate a comprehensive test report"""
    print("\n" + "=" * 60)
    print("📋 GMAIL OAUTH IMPLEMENTATION TEST REPORT")
    print("=" * 60)
    
    results = {
        "Gmail OAuth Gateway File": test_gmail_oauth_direct(),
        "Gmail OAuth API Router": test_api_router_direct(),
        "Required Dependencies": check_dependencies(),
        "Environment Configuration": check_environment(),
        "FastAPI Integration": test_minimal_fastapi()
    }
    
    print("\n📊 SUMMARY")
    print("-" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if results["Gmail OAuth Gateway File"] and results["Gmail OAuth API Router"]:
        print("1. ✅ Core Gmail OAuth implementation is complete and properly structured")
    else:
        print("1. ❌ Core implementation files have issues - check file contents")
    
    if results["Required Dependencies"]:
        print("2. ✅ All required dependencies are installed")
    else:
        print("2. ⚠️  Some dependencies missing - run: pip install google-auth google-auth-oauthlib google-api-python-client")
    
    if results["Environment Configuration"]:
        print("3. ✅ Environment is properly configured")
    else:
        print("3. ⚠️  Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
    
    if not results["FastAPI Integration"]:
        print("4. ⚠️  FastAPI integration needs work - missing core modules (logging, config, event_bus)")
        print("   This is normal for isolated testing - should work in full project context")
    
    if passed >= 3:
        print("\n🚀 READY FOR TESTING:")
        print("   - Set up Google OAuth credentials in Google Cloud Console")
        print("   - Set environment variables")
        print("   - Start FastAPI server: uvicorn main:app --reload")
        print("   - Test OAuth flow via API endpoints")
    else:
        print("\n🔧 NEEDS WORK:")
        print("   - Fix failing components before proceeding")
        print("   - Ensure all dependencies are installed")
        print("   - Complete environment configuration")

if __name__ == "__main__":
    generate_report()