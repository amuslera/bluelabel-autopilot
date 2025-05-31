"""
E2E security tests for the application.
Tests authentication, authorization, XSS, CSRF, and other security measures.
"""
import pytest
from playwright.sync_api import Page, expect
import re
from typing import Dict


class TestSecurityMeasures:
    """Test application security measures."""
    
    @pytest.fixture
    def test_credentials(self) -> Dict[str, str]:
        """Return test user credentials."""
        return {
            "valid_user": {"email": "user@example.com", "password": "ValidPass123!"},
            "admin_user": {"email": "admin@example.com", "password": "AdminPass123!"},
            "attacker": {"email": "attacker@evil.com", "password": "HackPass123!"}
        }
    
    def test_authentication_required(self, page: Page):
        """Test protected routes require authentication."""
        protected_routes = [
            "/dashboard",
            "/my-agents",
            "/profile",
            "/settings",
            "/api/user/profile",
            "/api/user/agents"
        ]
        
        for route in protected_routes:
            page.goto(route)
            
            # Should redirect to login or show 401
            if route.startswith("/api"):
                # API routes should return 401
                response = page.request.get(route)
                assert response.status == 401, f"{route} should return 401 for unauthenticated requests"
            else:
                # UI routes should redirect to login
                expect(page).to_have_url(re.compile("/login"))
    
    def test_sql_injection_prevention(self, page: Page):
        """Test SQL injection prevention in forms."""
        page.goto("/login")
        
        # Common SQL injection attempts
        sql_injections = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "' OR 1=1 --",
            "admin' /*",
            "\\'; DROP TABLE users; --"
        ]
        
        for injection in sql_injections:
            page.fill('input[name="email"]', injection)
            page.fill('input[name="password"]', "password")
            page.click('button[type="submit"]')
            
            page.wait_for_load_state("networkidle")
            
            # Should show error, not succeed or crash
            error_message = page.locator("text=/invalid|error|failed/i")
            expect(error_message).to_be_visible()
            
            # Should still be on login page
            expect(page).to_have_url(re.compile("/login"))
    
    def test_xss_prevention(self, page: Page):
        """Test Cross-Site Scripting (XSS) prevention."""
        # Test various XSS payloads in different contexts
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert(String.fromCharCode(88,83,83))</script>"
        ]
        
        # Test in search
        page.goto("/marketplace")
        search_input = page.locator('input[type="search"]')
        
        for payload in xss_payloads:
            search_input.fill(payload)
            search_input.press("Enter")
            
            page.wait_for_load_state("networkidle")
            
            # Check no alerts triggered
            # In Playwright, alerts would cause the test to fail if not handled
            
            # Check payload is escaped in output
            page_content = page.content()
            assert "<script>" not in page_content or "&lt;script&gt;" in page_content, \
                "Script tags should be escaped"
    
    def test_csrf_protection(self, page: Page, test_credentials: Dict[str, str]):
        """Test CSRF protection on state-changing operations."""
        # Login first
        user = test_credentials["valid_user"]
        page.goto("/login")
        page.fill('input[name="email"]', user["email"])
        page.fill('input[name="password"]', user["password"])
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Try to make a state-changing request without CSRF token
        response = page.request.post("/api/agents/install", 
                                   data={"agent_id": "test-agent"},
                                   headers={"Content-Type": "application/json"})
        
        # Should be rejected without proper CSRF token
        assert response.status in [400, 403], "POST request without CSRF token should be rejected"
    
    def test_password_security_requirements(self, page: Page):
        """Test password security requirements."""
        page.goto("/register")
        
        weak_passwords = [
            "password",     # Too common
            "12345678",     # No letters
            "abcdefgh",     # No numbers
            "Pass123",      # Too short
            "password123",  # No special chars/uppercase
        ]
        
        for weak_pass in weak_passwords:
            page.fill('input[name="email"]', "test@example.com")
            page.fill('input[name="password"]', weak_pass)
            page.fill('input[name="confirmPassword"]', weak_pass)
            page.click('button[type="submit"]')
            
            # Should show password strength error
            error = page.locator("text=/weak|strong|requirement/i")
            expect(error).to_be_visible()
            
            # Should not proceed
            expect(page).to_have_url(re.compile("/register"))
    
    def test_session_security(self, page: Page, test_credentials: Dict[str, str], context):
        """Test session security measures."""
        # Login
        user = test_credentials["valid_user"]
        page.goto("/login")
        page.fill('input[name="email"]', user["email"])
        page.fill('input[name="password"]', user["password"])
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Check session cookie security flags
        cookies = context.cookies()
        session_cookie = next((c for c in cookies if "session" in c["name"].lower() 
                             or "token" in c["name"].lower()), None)
        
        if session_cookie:
            # Should have security flags
            assert session_cookie.get("httpOnly"), "Session cookie should be httpOnly"
            assert session_cookie.get("secure") or "localhost" in session_cookie["domain"], \
                "Session cookie should be secure (except localhost)"
            assert session_cookie.get("sameSite") in ["Strict", "Lax"], \
                "Session cookie should have SameSite attribute"
    
    def test_rate_limiting(self, page: Page):
        """Test rate limiting on sensitive endpoints."""
        # Try multiple failed login attempts
        page.goto("/login")
        
        for i in range(10):
            page.fill('input[name="email"]', "test@example.com")
            page.fill('input[name="password"]', f"WrongPass{i}")
            page.click('button[type="submit"]')
            page.wait_for_timeout(100)  # Small delay between attempts
        
        # After multiple attempts, should see rate limit message or captcha
        rate_limit_msg = page.locator("text=/too many|rate limit|try again later/i")
        captcha = page.locator('[data-testid="captcha"], .g-recaptcha')
        
        assert rate_limit_msg.is_visible() or captcha.is_visible(), \
            "Should implement rate limiting after multiple failed attempts"
    
    def test_authorization_levels(self, page: Page, test_credentials: Dict[str, str]):
        """Test different authorization levels."""
        # Login as regular user
        user = test_credentials["valid_user"]
        page.goto("/login")
        page.fill('input[name="email"]', user["email"])
        page.fill('input[name="password"]', user["password"])
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Try to access admin routes
        admin_routes = ["/admin", "/api/admin/users", "/api/admin/agents"]
        
        for route in admin_routes:
            if route.startswith("/api"):
                response = page.request.get(route)
                assert response.status in [403, 404], \
                    f"Regular user should not access {route}"
            else:
                page.goto(route)
                # Should either redirect or show forbidden
                assert page.url != route, f"Regular user should not access {route}"
    
    def test_input_sanitization(self, page: Page):
        """Test input sanitization across forms."""
        page.goto("/register")
        
        # Test various malicious inputs
        malicious_inputs = [
            "user@evil.com<script>alert('xss')</script>",
            "user+tag@example.com",  # Valid but often problematic
            "user@example.com%00",  # Null byte
            "user@example.com\r\nBcc: attacker@evil.com",  # Email header injection
        ]
        
        for input_val in malicious_inputs:
            page.fill('input[name="email"]', input_val)
            page.fill('input[name="password"]', "ValidPass123!")
            page.fill('input[name="confirmPassword"]', "ValidPass123!")
            page.click('button[type="submit"]')
            
            page.wait_for_load_state("networkidle")
            
            # Should either sanitize or reject
            # Check we're still on register or got an error
            assert page.url.endswith("/register") or \
                   page.locator("text=/invalid|error/i").is_visible()
    
    def test_file_upload_security(self, page: Page, test_credentials: Dict[str, str]):
        """Test file upload security measures."""
        # Login first
        user = test_credentials["valid_user"]
        page.goto("/login")
        page.fill('input[name="email"]', user["email"])
        page.fill('input[name="password"]', user["password"])
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Navigate to a page with file upload
        page.goto("/profile")
        
        file_input = page.locator('input[type="file"]')
        if file_input.is_visible():
            # Test file type restrictions
            # This would normally use actual files
            # Here we're checking the accept attribute
            accept_attr = file_input.get_attribute("accept")
            if accept_attr:
                assert "image/" in accept_attr or ".jpg" in accept_attr, \
                    "File upload should restrict file types"
    
    def test_api_authentication_tokens(self, page: Page, test_credentials: Dict[str, str]):
        """Test API authentication token handling."""
        # Get auth token
        user = test_credentials["valid_user"]
        page.goto("/login")
        page.fill('input[name="email"]', user["email"])
        page.fill('input[name="password"]', user["password"])
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Extract token
        token = page.evaluate("() => localStorage.getItem('authToken') || ''")
        
        if token:
            # Test invalid token
            response = page.request.get("/api/user/profile", 
                                      headers={"Authorization": "Bearer invalid-token"})
            assert response.status == 401, "Invalid token should be rejected"
            
            # Test expired token format
            response = page.request.get("/api/user/profile",
                                      headers={"Authorization": "Bearer " + token[:10]})
            assert response.status == 401, "Malformed token should be rejected"
    
    def test_clickjacking_protection(self, page: Page):
        """Test clickjacking protection headers."""
        response = page.goto("/")
        
        # Check security headers
        headers = response.headers
        
        # X-Frame-Options or CSP frame-ancestors
        x_frame = headers.get("x-frame-options", "").lower()
        csp = headers.get("content-security-policy", "").lower()
        
        assert x_frame in ["deny", "sameorigin"] or "frame-ancestors" in csp, \
            "Should have clickjacking protection headers"
    
    def test_secure_headers(self, page: Page):
        """Test presence of security headers."""
        response = page.goto("/")
        headers = response.headers
        
        # Check important security headers
        security_headers = {
            "x-content-type-options": "nosniff",
            "x-xss-protection": "1; mode=block",
            "strict-transport-security": "max-age=",
            "referrer-policy": ["no-referrer", "strict-origin", "same-origin"]
        }
        
        for header, expected in security_headers.items():
            value = headers.get(header, "").lower()
            if isinstance(expected, list):
                assert any(exp in value for exp in expected), \
                    f"Missing or incorrect {header} header"
            else:
                assert expected in value, f"Missing or incorrect {header} header"