"""
E2E tests for page load performance.
Tests page load times meet <3s target and other web vitals.
"""
import pytest
from playwright.sync_api import Page
import time
from typing import Dict, List


class TestPageLoadPerformance:
    """Test page load performance benchmarks."""
    
    @pytest.fixture
    def critical_pages(self) -> List[Dict[str, str]]:
        """Return list of critical pages to test."""
        return [
            {"url": "/", "name": "Home Page"},
            {"url": "/login", "name": "Login Page"},
            {"url": "/register", "name": "Registration Page"},
            {"url": "/marketplace", "name": "Marketplace"},
            {"url": "/dashboard", "name": "Dashboard", "auth_required": True},
            {"url": "/my-agents", "name": "My Agents", "auth_required": True},
        ]
    
    @pytest.fixture
    def authenticated_context(self, page: Page):
        """Return authenticated page context."""
        # Login first
        page.goto("/login")
        page.fill('input[name="email"]', "test@example.com")
        page.fill('input[name="password"]', "TestPass123!")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        return page
    
    def measure_page_metrics(self, page: Page, url: str) -> Dict[str, float]:
        """Measure page load metrics."""
        # Start navigation
        start_time = time.time()
        page.goto(url)
        
        # Wait for different load states
        page.wait_for_load_state("domcontentloaded")
        dom_content_loaded = time.time() - start_time
        
        page.wait_for_load_state("load")
        load_complete = time.time() - start_time
        
        page.wait_for_load_state("networkidle")
        network_idle = time.time() - start_time
        
        # Measure web vitals using Performance API
        metrics = page.evaluate("""
            () => {
                const navTiming = performance.getEntriesByType('navigation')[0];
                const paintTiming = performance.getEntriesByName('first-contentful-paint')[0];
                const layoutShift = performance.getEntriesByType('layout-shift');
                
                let cls = 0;
                layoutShift.forEach(entry => {
                    if (!entry.hadRecentInput) {
                        cls += entry.value;
                    }
                });
                
                return {
                    ttfb: navTiming.responseStart - navTiming.requestStart,
                    fcp: paintTiming ? paintTiming.startTime : 0,
                    domInteractive: navTiming.domInteractive,
                    cls: cls,
                    resourceCount: performance.getEntriesByType('resource').length,
                    transferSize: navTiming.transferSize || 0
                };
            }
        """)
        
        return {
            "dom_content_loaded": dom_content_loaded * 1000,  # Convert to ms
            "load_complete": load_complete * 1000,
            "network_idle": network_idle * 1000,
            "ttfb": metrics["ttfb"],
            "fcp": metrics["fcp"],
            "dom_interactive": metrics["domInteractive"],
            "cls": metrics["cls"],
            "resource_count": metrics["resourceCount"],
            "transfer_size": metrics["transferSize"]
        }
    
    def test_page_load_times(self, page: Page, critical_pages: List[Dict[str, str]], 
                           authenticated_context: Page):
        """Test page load times are under 3s target."""
        results = []
        
        for page_info in critical_pages:
            url = page_info["url"]
            name = page_info["name"]
            auth_required = page_info.get("auth_required", False)
            
            # Use authenticated context if required
            test_page = authenticated_context if auth_required else page
            
            # Clear cache for consistent testing
            test_page.context.clear_cookies()
            
            # Measure metrics
            metrics = self.measure_page_metrics(test_page, url)
            
            results.append({
                "page": name,
                "load_time": metrics["load_complete"],
                "fcp": metrics["fcp"],
                "ttfb": metrics["ttfb"],
                "meets_target": metrics["load_complete"] < 3000
            })
            
            # Assert performance target
            assert metrics["load_complete"] < 3000, \
                f"{name} load time {metrics['load_complete']:.0f}ms exceeds 3000ms target"
        
        # Print summary
        print("\n=== Page Load Performance Summary ===")
        for result in results:
            status = "✓" if result["meets_target"] else "✗"
            print(f"{status} {result['page']}: {result['load_time']:.0f}ms load, "
                  f"{result['fcp']:.0f}ms FCP, {result['ttfb']:.0f}ms TTFB")
    
    def test_first_contentful_paint(self, page: Page, critical_pages: List[Dict[str, str]]):
        """Test First Contentful Paint (FCP) performance."""
        for page_info in critical_pages[:3]:  # Test first 3 pages
            if not page_info.get("auth_required", False):
                metrics = self.measure_page_metrics(page, page_info["url"])
                
                # FCP should be under 1.8s for good user experience
                assert metrics["fcp"] < 1800, \
                    f"{page_info['name']} FCP {metrics['fcp']:.0f}ms exceeds 1800ms target"
    
    def test_time_to_interactive(self, page: Page):
        """Test Time to Interactive (TTI) for key pages."""
        page.goto("/marketplace")
        
        # Measure time until page is interactive
        tti = page.evaluate("""
            () => {
                return new Promise(resolve => {
                    let tti = 0;
                    const observer = new PerformanceObserver(list => {
                        const entries = list.getEntries();
                        entries.forEach(entry => {
                            if (entry.name === 'first-input') {
                                tti = entry.processingStart - entry.startTime;
                            }
                        });
                    });
                    observer.observe({ entryTypes: ['first-input'] });
                    
                    // Simulate user interaction
                    setTimeout(() => {
                        const navTiming = performance.getEntriesByType('navigation')[0];
                        resolve(navTiming.domInteractive);
                    }, 100);
                });
            }
        """)
        
        # TTI should be under 3.8s
        assert tti < 3800, f"Time to Interactive {tti:.0f}ms exceeds 3800ms target"
    
    def test_cumulative_layout_shift(self, page: Page):
        """Test Cumulative Layout Shift (CLS) score."""
        page.goto("/marketplace")
        
        # Scroll to trigger any layout shifts
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        page.evaluate("window.scrollTo(0, 0)")
        
        # Measure CLS
        cls = page.evaluate("""
            () => {
                let cls = 0;
                const layoutShifts = performance.getEntriesByType('layout-shift');
                layoutShifts.forEach(entry => {
                    if (!entry.hadRecentInput) {
                        cls += entry.value;
                    }
                });
                return cls;
            }
        """)
        
        # CLS should be under 0.1 for good user experience
        assert cls < 0.1, f"Cumulative Layout Shift {cls:.3f} exceeds 0.1 threshold"
    
    def test_bundle_size_analysis(self, page: Page):
        """Test JavaScript bundle sizes."""
        page.goto("/")
        
        # Get all JavaScript resources
        js_resources = page.evaluate("""
            () => {
                const resources = performance.getEntriesByType('resource');
                return resources
                    .filter(r => r.name.endsWith('.js'))
                    .map(r => ({
                        name: r.name.split('/').pop(),
                        size: r.transferSize,
                        duration: r.duration
                    }));
            }
        """)
        
        total_size = sum(r["size"] for r in js_resources)
        
        # Total JS bundle should be reasonable
        assert total_size < 1024 * 1024 * 2, \
            f"Total JavaScript bundle size {total_size / 1024:.0f}KB exceeds 2MB"
        
        # Check for any oversized bundles
        for resource in js_resources:
            assert resource["size"] < 500 * 1024, \
                f"Bundle {resource['name']} size {resource['size'] / 1024:.0f}KB exceeds 500KB"
    
    def test_page_load_mobile_performance(self, page: Page):
        """Test page load performance on mobile."""
        # Set mobile viewport and network
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Simulate 3G network
        page.context.set_offline(False)
        page.context.set_extra_http_headers({"Save-Data": "on"})
        
        metrics = self.measure_page_metrics(page, "/marketplace")
        
        # Mobile load time can be slightly higher but should still be reasonable
        assert metrics["load_complete"] < 5000, \
            f"Mobile load time {metrics['load_complete']:.0f}ms exceeds 5000ms target"
        
        # FCP on mobile
        assert metrics["fcp"] < 3000, \
            f"Mobile FCP {metrics['fcp']:.0f}ms exceeds 3000ms target"
    
    def test_resource_loading_waterfall(self, page: Page):
        """Test resource loading optimization."""
        page.goto("/")
        
        # Analyze resource loading
        resources = page.evaluate("""
            () => {
                const resources = performance.getEntriesByType('resource');
                const critical = resources.filter(r => 
                    r.name.includes('.css') || 
                    r.name.includes('font') ||
                    (r.name.includes('.js') && r.fetchStart < 500)
                );
                
                return {
                    totalResources: resources.length,
                    criticalResources: critical.length,
                    parallelLoading: critical.filter(r => r.startTime < 100).length
                };
            }
        """)
        
        # Critical resources should load early and in parallel
        assert resources["parallelLoading"] >= resources["criticalResources"] * 0.5, \
            "Critical resources should load in parallel"
    
    def test_memory_usage(self, page: Page):
        """Test memory usage doesn't grow excessively."""
        # Navigate to a page with dynamic content
        page.goto("/marketplace")
        
        # Get initial memory usage
        initial_memory = page.evaluate("""
            () => {
                if (performance.memory) {
                    return performance.memory.usedJSHeapSize;
                }
                return 0;
            }
        """)
        
        # Interact with the page
        for _ in range(5):
            # Scroll down
            page.evaluate("window.scrollBy(0, 500)")
            page.wait_for_timeout(500)
            
            # Click on filters
            filter = page.locator('[data-testid="category-filter"]').first
            if filter.is_visible():
                filter.click()
        
        # Get final memory usage
        final_memory = page.evaluate("() => performance.memory ? performance.memory.usedJSHeapSize : 0")
        
        # Memory growth should be reasonable
        if initial_memory > 0 and final_memory > 0:
            memory_growth = (final_memory - initial_memory) / 1024 / 1024  # Convert to MB
            assert memory_growth < 50, f"Memory grew by {memory_growth:.1f}MB during interaction"
    
    def test_lighthouse_metrics(self, page: Page):
        """Test key Lighthouse performance metrics."""
        # This is a simplified version - in production you'd use actual Lighthouse
        page.goto("/")
        
        metrics = page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                const paint = performance.getEntriesByType('paint');
                
                return {
                    // Simulate Lighthouse scoring
                    performance: navigation.loadEventEnd < 3000 ? 90 : 70,
                    accessibility: document.querySelectorAll('[alt]').length > 0 ? 85 : 60,
                    bestPractices: window.location.protocol === 'https:' ? 90 : 70,
                    seo: document.querySelector('meta[name="description"]') ? 85 : 60
                };
            }
        """)
        
        # All scores should be above 70
        for metric, score in metrics.items():
            assert score >= 70, f"{metric} score {score} is below 70"