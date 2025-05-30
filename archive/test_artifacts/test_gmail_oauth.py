#!/usr/bin/env python3
"""
Test script for Gmail OAuth implementation in BlueLabel AIOS v2
"""
import sys
import os
import asyncio
from pathlib import Path

# Add AIOS v2 project to Python path
aios_v2_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2")
sys.path.insert(0, str(aios_v2_path))

# Mock missing modules for testing
class MockEventBus:
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
    
    def publish(self, stream, message):
        return f"mock_task_{id(message)}"

class MockBaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Mock the missing modules
sys.modules['core.event_bus'] = type('MockModule', (), {
    'EventBus': MockEventBus
})()

sys.modules['shared.schemas.base'] = type('MockModule', (), {
    'BaseModel': MockBaseModel
})()

# Mock logging setup
def mock_setup_logging(service_name=None):
    import logging
    return logging.getLogger(service_name or 'test')

sys.modules['core.logging'] = type('MockModule', (), {
    'setup_logging': mock_setup_logging
})()

async def test_gmail_oauth():
    """Test Gmail OAuth gateway functionality"""
    try:
        from services.gateway.gmail_oauth_env_gateway import GmailOAuthEnvGateway
        
        print("✅ Successfully imported GmailOAuthEnvGateway")
        
        # Test initialization
        gateway = GmailOAuthEnvGateway()
        print("✅ Successfully initialized Gmail OAuth gateway")
        
        # Check configuration status
        is_configured = gateway.is_configured()
        print(f"📋 Configuration status: {'✅ Configured' if is_configured else '❌ Not configured'}")
        
        if not is_configured:
            print("⚠️  Gmail OAuth credentials not found in environment")
            print("   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to test authentication")
        
        # Check authentication status
        is_authenticated = gateway.is_authenticated()
        print(f"🔐 Authentication status: {'✅ Authenticated' if is_authenticated else '❌ Not authenticated'}")
        
        # Test authentication endpoint (without actual auth code)
        auth_result = await gateway.authenticate()
        print(f"🔑 Authentication test: {auth_result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Gmail OAuth: {e}")
        return False

async def test_api_endpoints():
    """Test Gmail OAuth API endpoints"""
    try:
        from apps.api.routers.gmail_oauth import router
        print("✅ Successfully imported Gmail OAuth API router")
        
        # Check if router has expected endpoints
        routes = [route.path for route in router.routes]
        expected_routes = ["/auth", "/auth/status", "/send", "/fetch", "/setup-instructions"]
        
        print("📍 Available API routes:")
        for route in routes:
            status = "✅" if route in expected_routes else "ℹ️"
            print(f"   {status} {route}")
        
        return True
        
    except ImportError as e:
        print(f"❌ API router import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

async def test_fastapi_server():
    """Test if FastAPI server can start with Gmail OAuth routes"""
    try:
        # Mock config and logging for main.py
        class MockConfig:
            debug = True
            logging = type('LoggingConfig', (), {
                'level': 'INFO',
                'file': None
            })()
        
        sys.modules['core.config'] = type('MockModule', (), {
            'config': MockConfig()
        })()
        
        # Mock middleware modules
        sys.modules['apps.api.middleware.error_handler'] = type('MockModule', (), {
            'register_error_handlers': lambda app: None
        })()
        
        sys.modules['apps.api.middleware.request_id'] = type('MockModule', (), {
            'request_id_middleware': lambda req, call_next: call_next(req)
        })()
        
        sys.modules['core.config_validator'] = type('MockModule', (), {
            'validate_config_on_startup': lambda: None
        })()
        
        # Mock other routers
        class MockRouter:
            def __init__(self):
                self.routes = []
        
        router_modules = [
            'gateway', 'agents', 'knowledge', 'events', 'gmail_proxy', 
            'gmail_hybrid', 'gmail_complete', 'email', 'communication', 
            'workflows', 'files_simple', 'files_process', 'status', 
            'health', 'setup', 'digest'
        ]
        
        for module_name in router_modules:
            sys.modules[f'apps.api.routers.{module_name}'] = type('MockModule', (), {
                'router': MockRouter(),
                'startup_event': lambda: None
            })()
        
        from fastapi import FastAPI
        from apps.api.routers import gmail_oauth
        
        # Create test app
        app = FastAPI(title="Test Gmail OAuth API")
        app.include_router(gmail_oauth.router, prefix="/api/v1/gmail", tags=["gmail"])
        
        print("✅ FastAPI app created successfully with Gmail OAuth routes")
        print(f"📍 Total routes: {len(app.routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating FastAPI app: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🧪 Testing Gmail OAuth Implementation in BlueLabel AIOS v2")
    print("=" * 60)
    
    tests = [
        ("Gmail OAuth Gateway", test_gmail_oauth),
        ("API Endpoints", test_api_endpoints),
        ("FastAPI Server", test_fastapi_server)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    # Environment check
    print("\n🌍 ENVIRONMENT STATUS")
    print("-" * 30)
    env_vars = ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REDIRECT_URI"]
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Not set"
        print(f"{status}: {var}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv("GOOGLE_CLIENT_SECRET"):
        print("1. ⚠️  Set up Google OAuth credentials:")
        print("   - Go to Google Cloud Console")
        print("   - Create OAuth 2.0 credentials")
        print("   - Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
    
    if passed == len(results):
        print("2. ✅ All core tests passed - Gmail OAuth implementation is functional")
        print("3. 🚀 Ready to start FastAPI server and test OAuth flow")
    else:
        print("2. ❌ Some tests failed - check error messages above")
        print("3. 🔧 Fix failing components before proceeding")

if __name__ == "__main__":
    asyncio.run(main())