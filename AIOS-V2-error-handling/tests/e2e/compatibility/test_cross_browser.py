"""
E2E tests for cross-browser compatibility.
Tests functionality across Chrome, Firefox, Safari, and Edge.
"""
import pytest
from playwright.sync_api import Page, expect, Browser
import re
from typing import List, Dict


class TestCrossBrowserCompatibility:
    """Test cross-browser compatibility."""
    
    @pytest.fixture(params=["chromium", "firefox", "webkit"])
    def browser_name(self, request):
        """Parameterized fixture for different browsers."""
        return request.param
    
    @pytest.fixture
    def multi_browser_page(self, browser_name, playwright) -> Page:
        """Create page for specific browser."""
        browser = getattr(playwright, browser_name).launch()
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()
    
    def test_basic_navigation(self, multi_browser_page: Page, browser_name: str):
        """Test basic navigation works across browsers."""
        page = multi_browser_page
        print(f"\nTesting on {browser_name}")
        
        # Navigate to home
        page.goto("/")
        expect(page).to_have_title(re.compile("Bluelabel|Agent|Marketplace"))
        
        # Navigate to marketplace
        marketplace_link = page.locator('a[href="/marketplace"], a:has-text("Marketplace")')
        marketplace_link.click()
        expect(page).to_have_url(re.compile("/marketplace"))
        
        # Navigate to login
        login_link = page.locator('a[href="/login"], a:has-text("Login")')
        login_link.click()
        expect(page).to_have_url(re.compile("/login"))
    
    def test_form_functionality(self, multi_browser_page: Page, browser_name: str):
        """Test form inputs work across browsers."""
        page = multi_browser_page
        page.goto("/register")
        
        # Test various input types
        email_input = page.locator('input[name="email"]')
        password_input = page.locator('input[name="password"]')
        confirm_input = page.locator('input[name="confirmPassword"]')
        
        # Fill form
        email_input.fill(f"{browser_name}@test.com")
        password_input.fill("TestPass123!")
        confirm_input.fill("TestPass123!")
        
        # Check values are set correctly
        expect(email_input).to_have_value(f"{browser_name}@test.com")
        expect(password_input).to_have_value("TestPass123!")
        
        # Test form submission
        submit_button = page.locator('button[type="submit"]')
        expect(submit_button).to_be_enabled()
    
    def test_javascript_functionality(self, multi_browser_page: Page, browser_name: str):
        """Test JavaScript features work across browsers."""
        page = multi_browser_page
        page.goto("/marketplace")
        
        # Test search autocomplete (JS-powered)
        search_input = page.locator('input[type="search"]')
        search_input.fill("con")
        
        # Wait for potential autocomplete
        page.wait_for_timeout(1000)
        
        # Test dynamic content loading
        initial_count = page.locator('[data-testid="agent-card"]').count()
        
        # Scroll to bottom to trigger infinite scroll if implemented
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        
        # Dynamic features should work
        final_count = page.locator('[data-testid="agent-card"]').count()
        assert final_count >= initial_count
    
    def test_css_rendering(self, multi_browser_page: Page, browser_name: str):
        """Test CSS renders correctly across browsers."""
        page = multi_browser_page
        page.goto("/")
        
        # Check key layout elements
        header = page.locator('header, [role="banner"]').first
        expect(header).to_be_visible()
        
        # Check flexbox/grid layouts
        if page.locator('.agent-grid, .grid').count() > 0:
            grid = page.locator('.agent-grid, .grid').first
            grid_box = grid.bounding_box()
            assert grid_box["width"] > 0 and grid_box["height"] > 0
        
        # Check CSS animations/transitions work
        button = page.locator('button').first
        if button.is_visible():
            # Hover to trigger any transitions
            button.hover()
            page.wait_for_timeout(100)
            # No JavaScript errors should occur
    
    def test_local_storage(self, multi_browser_page: Page, browser_name: str):
        """Test localStorage works across browsers."""
        page = multi_browser_page
        page.goto("/")
        
        # Set localStorage item
        page.evaluate("localStorage.setItem('testKey', 'testValue')")
        
        # Retrieve and verify
        value = page.evaluate("localStorage.getItem('testKey')")
        assert value == "testValue", f"localStorage not working in {browser_name}"
        
        # Test persistence
        page.reload()
        value_after_reload = page.evaluate("localStorage.getItem('testKey')")
        assert value_after_reload == "testValue"
    
    def test_responsive_design(self, multi_browser_page: Page, browser_name: str):
        """Test responsive design across browsers."""
        page = multi_browser_page
        
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"}
        ]
        
        for viewport in viewports:
            page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
            page.goto("/marketplace")
            
            # Check elements adapt
            agent_cards = page.locator('[data-testid="agent-card"]')
            if agent_cards.count() > 1:
                first_card = agent_cards.first.bounding_box()
                second_card = agent_cards.nth(1).bounding_box()
                
                if viewport["name"] == "Mobile":
                    # Cards should stack vertically
                    assert second_card["y"] > first_card["y"]
                else:
                    # Cards should be in grid
                    assert second_card["x"] > first_card["x"] or second_card["y"] > first_card["y"]
    
    def test_media_elements(self, multi_browser_page: Page, browser_name: str):
        """Test media elements work across browsers."""
        page = multi_browser_page
        page.goto("/")
        
        # Test images load
        images = page.locator('img')
        if images.count() > 0:
            for i in range(min(3, images.count())):
                img = images.nth(i)
                if img.is_visible():
                    # Check image loaded
                    loaded = page.evaluate("""
                        (img) => img.complete && img.naturalHeight !== 0
                    """, img)
                    assert loaded, f"Image not loading in {browser_name}"
        
        # Test video elements if present
        videos = page.locator('video')
        if videos.count() > 0:
            video = videos.first
            # Check video can be played
            can_play = page.evaluate("(video) => video.canPlayType('video/mp4') !== ''", video)
            assert can_play, f"Video support missing in {browser_name}"
    
    def test_ajax_requests(self, multi_browser_page: Page, browser_name: str):
        """Test AJAX/fetch requests work across browsers."""
        page = multi_browser_page
        page.goto("/marketplace")
        
        # Intercept API calls
        api_calls = []
        page.on("request", lambda req: api_calls.append(req) if "/api/" in req.url else None)
        
        # Trigger an action that makes API call
        search_input = page.locator('input[type="search"]')
        if search_input.is_visible():
            search_input.fill("test")
            search_input.press("Enter")
            page.wait_for_load_state("networkidle")
            
            # Check API calls were made
            assert len([r for r in api_calls if "search" in r.url or "agents" in r.url]) > 0, \
                f"API calls not working in {browser_name}"
    
    def test_browser_specific_features(self, multi_browser_page: Page, browser_name: str):
        """Test browser-specific feature compatibility."""
        page = multi_browser_page
        page.goto("/")
        
        # Test features that might vary between browsers
        features_support = page.evaluate("""
            () => ({
                webgl: !!window.WebGLRenderingContext,
                websocket: 'WebSocket' in window,
                serviceWorker: 'serviceWorker' in navigator,
                indexedDB: !!window.indexedDB,
                webAudio: 'AudioContext' in window || 'webkitAudioContext' in window,
                geolocation: 'geolocation' in navigator,
                notifications: 'Notification' in window
            })
        """)
        
        # Core features should be supported
        assert features_support["websocket"], f"WebSocket not supported in {browser_name}"
        assert features_support["indexedDB"], f"IndexedDB not supported in {browser_name}"
    
    @pytest.mark.parametrize("browser_version", [
        {"browser": "chromium", "version": "90"},
        {"browser": "firefox", "version": "88"},
        {"browser": "webkit", "version": "14"}
    ])
    def test_older_browser_versions(self, page: Page, browser_version: Dict[str, str]):
        """Test compatibility with older browser versions."""
        # This test would normally use specific browser versions
        # For now, we test fallbacks and polyfills
        page.goto("/")
        
        # Check for polyfills
        polyfills = page.evaluate("""
            () => ({
                promise: typeof Promise !== 'undefined',
                fetch: typeof fetch !== 'undefined',
                objectAssign: typeof Object.assign !== 'undefined',
                arrayIncludes: typeof Array.prototype.includes !== 'undefined'
            })
        """)
        
        # Essential features should work (via polyfills if needed)
        for feature, supported in polyfills.items():
            assert supported, f"{feature} not supported/polyfilled"
    
    def test_console_errors(self, multi_browser_page: Page, browser_name: str):
        """Test for console errors across browsers."""
        page = multi_browser_page
        
        # Collect console messages
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
        
        # Navigate through key pages
        pages_to_test = ["/", "/marketplace", "/login", "/register"]
        
        for url in pages_to_test:
            page.goto(url)
            page.wait_for_load_state("networkidle")
        
        # Check for JavaScript errors
        assert len(console_errors) == 0, \
            f"Console errors in {browser_name}: {[err.text for err in console_errors]}"
    
    def test_browser_specific_css(self, multi_browser_page: Page, browser_name: str):
        """Test CSS vendor prefixes and browser-specific styles."""
        page = multi_browser_page
        page.goto("/")
        
        # Check for CSS features that might need prefixes
        css_support = page.evaluate("""
            () => {
                const el = document.createElement('div');
                const styles = window.getComputedStyle(el);
                
                return {
                    flexbox: 'flex' in el.style || 'webkitFlex' in el.style,
                    grid: 'grid' in el.style,
                    transform: 'transform' in el.style || 'webkitTransform' in el.style,
                    transition: 'transition' in el.style || 'webkitTransition' in el.style,
                    animation: 'animation' in el.style || 'webkitAnimation' in el.style
                };
            }
        """)
        
        # Modern CSS features should be supported
        for feature, supported in css_support.items():
            assert supported, f"CSS {feature} not supported in {browser_name}"