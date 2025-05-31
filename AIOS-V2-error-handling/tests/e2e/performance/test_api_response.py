"""
E2E tests for API response time performance.
Tests API endpoints meet <200ms response time target.
"""
import pytest
from playwright.sync_api import Page, APIResponse
import time
import statistics
from typing import List, Dict


class TestAPIResponsePerformance:
    """Test API response time performance benchmarks."""
    
    @pytest.fixture
    def api_endpoints(self) -> List[Dict[str, str]]:
        """Return list of API endpoints to test."""
        return [
            {"method": "GET", "endpoint": "/api/agents", "name": "List Agents"},
            {"method": "GET", "endpoint": "/api/agents/popular", "name": "Popular Agents"},
            {"method": "GET", "endpoint": "/api/agents/categories", "name": "Agent Categories"},
            {"method": "GET", "endpoint": "/api/user/profile", "name": "User Profile"},
            {"method": "GET", "endpoint": "/api/user/agents", "name": "User's Agents"},
            {"method": "GET", "endpoint": "/api/marketplace/search?q=test", "name": "Search"},
            {"method": "GET", "endpoint": "/api/health", "name": "Health Check"},
        ]
    
    @pytest.fixture
    def auth_token(self, page: Page) -> str:
        """Get authentication token for API requests."""
        # Login to get token
        page.goto("/login")
        page.fill('input[name="email"]', "test@example.com")
        page.fill('input[name="password"]', "TestPass123!")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Extract token from localStorage or cookies
        token = page.evaluate("() => localStorage.getItem('authToken') || ''")
        if not token:
            # Try from cookies
            cookies = page.context.cookies()
            auth_cookie = next((c for c in cookies if "token" in c["name"].lower()), None)
            if auth_cookie:
                token = auth_cookie["value"]
        
        return token
    
    def measure_response_time(self, page: Page, method: str, endpoint: str, 
                            headers: Dict[str, str] = None) -> float:
        """Measure response time for a single API request."""
        start_time = time.time()
        
        if method == "GET":
            response = page.request.get(endpoint, headers=headers)
        elif method == "POST":
            response = page.request.post(endpoint, headers=headers)
        else:
            response = page.request.fetch(endpoint, method=method, headers=headers)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return response_time
    
    def test_api_response_times(self, page: Page, api_endpoints: List[Dict[str, str]], auth_token: str):
        """Test API response times are under 200ms target."""
        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        results = []
        
        for endpoint_info in api_endpoints:
            method = endpoint_info["method"]
            endpoint = endpoint_info["endpoint"]
            name = endpoint_info["name"]
            
            # Warm up request
            self.measure_response_time(page, method, base_url + endpoint, headers)
            
            # Measure multiple times
            response_times = []
            for _ in range(5):
                response_time = self.measure_response_time(page, method, base_url + endpoint, headers)
                response_times.append(response_time)
            
            avg_time = statistics.mean(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
            
            results.append({
                "endpoint": name,
                "avg_time": avg_time,
                "p95_time": p95_time,
                "meets_target": avg_time < 200
            })
            
            # Assert performance target
            assert avg_time < 200, f"{name} average response time {avg_time:.1f}ms exceeds 200ms target"
        
        # Print summary
        print("\n=== API Performance Summary ===")
        for result in results:
            status = "✓" if result["meets_target"] else "✗"
            print(f"{status} {result['endpoint']}: {result['avg_time']:.1f}ms avg, {result['p95_time']:.1f}ms p95")
    
    def test_concurrent_api_requests(self, page: Page, auth_token: str):
        """Test API performance under concurrent load."""
        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        # Test concurrent requests to same endpoint
        endpoint = "/api/agents"
        concurrent_count = 10
        
        import asyncio
        
        async def make_concurrent_requests():
            tasks = []
            for _ in range(concurrent_count):
                task = page.request.get(base_url + endpoint, headers=headers)
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            return (end_time - start_time) * 1000, responses
        
        # Run concurrent requests
        total_time, responses = asyncio.run(make_concurrent_requests())
        avg_time = total_time / concurrent_count
        
        # Check all requests succeeded
        for response in responses:
            assert response.status < 400, f"Request failed with status {response.status}"
        
        # Check performance didn't degrade significantly
        assert avg_time < 400, f"Average response time {avg_time:.1f}ms under load exceeds acceptable threshold"
    
    def test_api_caching_performance(self, page: Page, auth_token: str):
        """Test API caching improves performance."""
        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        endpoint = "/api/agents/popular"
        
        # First request (cache miss)
        first_time = self.measure_response_time(page, "GET", base_url + endpoint, headers)
        
        # Second request (potential cache hit)
        second_time = self.measure_response_time(page, "GET", base_url + endpoint, headers)
        
        # Third request (should be cached)
        third_time = self.measure_response_time(page, "GET", base_url + endpoint, headers)
        
        # Cached requests should be faster
        assert third_time <= first_time, "Cached requests should not be slower than initial request"
        
        # If caching is implemented, subsequent requests should be significantly faster
        if third_time < first_time * 0.5:
            print(f"✓ Caching detected: {first_time:.1f}ms -> {third_time:.1f}ms")
    
    def test_api_error_response_performance(self, page: Page):
        """Test error responses are also performant."""
        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
        
        # Test 404 response time
        not_found_time = self.measure_response_time(page, "GET", base_url + "/api/nonexistent")
        assert not_found_time < 200, f"404 response time {not_found_time:.1f}ms exceeds target"
        
        # Test unauthorized response time
        unauth_time = self.measure_response_time(page, "GET", base_url + "/api/user/profile")
        assert unauth_time < 200, f"401 response time {unauth_time:.1f}ms exceeds target"
        
        # Test bad request response time
        bad_request_time = self.measure_response_time(page, "POST", base_url + "/api/agents", 
                                                     {"Content-Type": "application/json"})
        assert bad_request_time < 200, f"400 response time {bad_request_time:.1f}ms exceeds target"
    
    def test_api_pagination_performance(self, page: Page, auth_token: str):
        """Test paginated endpoint performance."""
        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        page_sizes = [10, 25, 50, 100]
        
        for size in page_sizes:
            endpoint = f"/api/agents?page=1&limit={size}"
            response_time = self.measure_response_time(page, "GET", base_url + endpoint, headers)
            
            # Larger pages can take slightly longer but should still be reasonable
            max_allowed = 200 + (size * 0.5)  # Allow 0.5ms per additional item
            assert response_time < max_allowed, \
                f"Response time {response_time:.1f}ms for {size} items exceeds threshold {max_allowed}ms"
    
    def test_api_search_performance(self, page: Page, auth_token: str):
        """Test search endpoint performance with various queries."""
        base_url = page.url.split('/')[0] + '//' + page.url.split('/')[2]
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        search_queries = [
            "a",  # Single character
            "test",  # Simple search
            "content management",  # Multi-word
            "workflow & automation",  # Special characters
            "very long search query with many words to test performance"  # Long query
        ]
        
        for query in search_queries:
            endpoint = f"/api/marketplace/search?q={query}"
            response_time = self.measure_response_time(page, "GET", base_url + endpoint, headers)
            
            # Search should still be fast
            assert response_time < 300, \
                f"Search response time {response_time:.1f}ms for query '{query}' exceeds 300ms threshold"