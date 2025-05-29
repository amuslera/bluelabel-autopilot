#!/usr/bin/env python3
"""
Minimal FastAPI server to test Gmail OAuth functionality
"""
import sys
import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Add AIOS v2 project to Python path
aios_v2_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2")
sys.path.insert(0, str(aios_v2_path))

# Mock the missing core modules
class MockEventBus:
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
    
    def publish(self, stream, message):
        print(f"📡 Event published to {stream}: {message.get('type', 'unknown')}")
        return f"mock_task_{id(message)}"

class MockBaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def mock_setup_logging(*args, **kwargs):
    """Mock logging setup - accepts any arguments"""
    service_name = None
    if args:
        service_name = args[0]
    if 'service_name' in kwargs:
        service_name = kwargs['service_name']
    if service_name is None:
        service_name = 'test'
    
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

# Set up mocks
sys.modules['core.event_bus'] = type('MockModule', (), {
    'EventBus': MockEventBus
})()

sys.modules['shared.schemas.base'] = type('MockModule', (), {
    'BaseModel': MockBaseModel
})()

sys.modules['core.logging'] = type('MockModule', (), {
    'setup_logging': mock_setup_logging
})()

# Now import the Gmail OAuth components
try:
    from services.gateway.gmail_oauth_env_gateway import GmailOAuthEnvGateway, GmailMessage
    print("✅ Successfully imported Gmail OAuth gateway")
except ImportError as e:
    print(f"❌ Failed to import Gmail OAuth gateway: {e}")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(
    title="Gmail OAuth Test Server",
    description="Test server for Gmail OAuth functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Gmail gateway instance
gmail_gateway = GmailOAuthEnvGateway()

# Request models
class AuthRequest(BaseModel):
    auth_code: Optional[str] = None

class EmailRequest(BaseModel):
    to: List[str]
    subject: str
    body: str
    html: bool = False
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None

class FetchRequest(BaseModel):
    query: str = "is:unread"
    max_results: int = 10

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Gmail OAuth Test Server",
        "status": "running",
        "endpoints": {
            "auth": "/auth",
            "auth_status": "/auth/status", 
            "send": "/send",
            "fetch": "/fetch",
            "setup": "/setup-instructions"
        }
    }

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gmail_configured": gmail_gateway.is_configured(),
        "gmail_authenticated": gmail_gateway.is_authenticated()
    }

# Gmail OAuth endpoints
@app.post("/auth")
async def authenticate(request: AuthRequest):
    """Authenticate with Gmail using OAuth 2.0"""
    result = await gmail_gateway.authenticate(auth_code=request.auth_code)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.get("/auth/status")
async def auth_status():
    """Check authentication status"""
    return {
        "configured": gmail_gateway.is_configured(),
        "authenticated": gmail_gateway.is_authenticated(),
        "token_file_exists": os.path.exists(gmail_gateway.token_file),
        "client_id_set": bool(os.getenv("GOOGLE_CLIENT_ID")),
        "client_secret_set": bool(os.getenv("GOOGLE_CLIENT_SECRET")),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob"),
        "environment_variables": {
            "GOOGLE_CLIENT_ID": "Set" if os.getenv("GOOGLE_CLIENT_ID") else "Not Set",
            "GOOGLE_CLIENT_SECRET": "Set" if os.getenv("GOOGLE_CLIENT_SECRET") else "Not Set",
            "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI", "Default"),
            "GMAIL_TOKEN_FILE": gmail_gateway.token_file
        }
    }

@app.post("/send")
async def send_email(request: EmailRequest):
    """Send an email via Gmail"""
    if not gmail_gateway.is_authenticated():
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please authenticate with Gmail first."
        )
    
    message = GmailMessage(
        to=request.to,
        subject=request.subject,
        body=request.body,
        html=request.html,
        cc=request.cc,
        bcc=request.bcc
    )
    
    result = await gmail_gateway.send_message(message)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.post("/fetch")
async def fetch_emails(request: FetchRequest):
    """Fetch emails from Gmail"""
    if not gmail_gateway.is_authenticated():
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please authenticate with Gmail first."
        )
    
    messages = await gmail_gateway.fetch_messages(
        query=request.query,
        max_results=request.max_results
    )
    
    return {
        "status": "success",
        "count": len(messages),
        "messages": messages
    }

@app.get("/setup-instructions")
async def setup_instructions():
    """Get Gmail OAuth setup instructions"""
    return {
        "title": "Gmail OAuth Setup Instructions",
        "steps": [
            "1. Go to Google Cloud Console (https://console.cloud.google.com/)",
            "2. Create a new project or select existing one",
            "3. Enable Gmail API for your project",
            "4. Go to APIs & Services > Credentials",
            "5. Create OAuth 2.0 credentials (Web application type)",
            "6. Add redirect URI: urn:ietf:wg:oauth:2.0:oob",
            "7. Copy the Client ID and Client Secret",
            "8. Set environment variables:",
            "   export GOOGLE_CLIENT_ID='your_client_id'",
            "   export GOOGLE_CLIENT_SECRET='your_client_secret'",
            "9. Restart this server",
            "10. Call POST /auth to start authentication",
            "11. Visit the returned URL to authorize access",
            "12. Copy the authorization code and call POST /auth with the code"
        ],
        "required_scopes": [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify"
        ],
        "environment_variables": {
            "GOOGLE_CLIENT_ID": "OAuth 2.0 Client ID (required)",
            "GOOGLE_CLIENT_SECRET": "OAuth 2.0 Client Secret (required)",
            "GOOGLE_REDIRECT_URI": "OAuth 2.0 Redirect URI (optional, defaults to urn:ietf:wg:oauth:2.0:oob)",
            "GMAIL_TOKEN_FILE": "Path to save OAuth token (optional, defaults to token.json)"
        },
        "test_endpoints": {
            "check_status": "GET /auth/status",
            "start_auth": "POST /auth (no body)",
            "complete_auth": "POST /auth {'auth_code': 'your_code'}",
            "send_email": "POST /send",
            "fetch_emails": "POST /fetch"
        },
        "current_status": {
            "configured": gmail_gateway.is_configured(),
            "authenticated": gmail_gateway.is_authenticated(),
            "client_id_set": bool(os.getenv("GOOGLE_CLIENT_ID")),
            "client_secret_set": bool(os.getenv("GOOGLE_CLIENT_SECRET"))
        }
    }

# Server startup message
@app.on_event("startup")
async def startup():
    print("\n🚀 Gmail OAuth Test Server Starting...")
    print("=" * 50)
    print(f"📍 Server URL: http://localhost:8000")
    print(f"📋 Documentation: http://localhost:8000/docs")
    print(f"🔧 Configuration status: {'✅ Configured' if gmail_gateway.is_configured() else '❌ Not configured'}")
    print(f"🔐 Authentication status: {'✅ Authenticated' if gmail_gateway.is_authenticated() else '❌ Not authenticated'}")
    
    if not gmail_gateway.is_configured():
        print("\n⚠️  SETUP REQUIRED:")
        print("   Visit http://localhost:8000/setup-instructions for setup guide")
        print("   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
    else:
        print("\n✅ Ready to test Gmail OAuth!")
        print("   Visit http://localhost:8000/docs to test API endpoints")

if __name__ == "__main__":
    import uvicorn
    
    print("🧪 Starting Gmail OAuth Test Server...")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )