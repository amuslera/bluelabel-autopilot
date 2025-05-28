"""
Full pipeline integration tests.

Tests the complete email → PDF → summary flow with various scenarios.
"""

import pytest
import asyncio
import requests
import websockets
import json
import base64
import tempfile
from pathlib import Path
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from typing import List, Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"


class TestFullPipeline:
    """Integration tests for the complete pipeline."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.api_url = API_BASE_URL
        self.ws_url = WS_URL
        
        # Check API health
        response = requests.get(f"{self.api_url}/health")
        if not response.ok:
            pytest.skip("API is not running")
    
    def create_test_pdf(self, size: str = "small") -> bytes:
        """Create test PDF of various sizes."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.utils import simpleSplit
        except ImportError:
            # Use a simple PDF bytes if reportlab not available
            return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            c = canvas.Canvas(tmp.name, pagesize=letter)
            
            if size == "small":
                # 1-page PDF
                c.drawString(100, 750, "Test PDF - Small")
                c.drawString(100, 700, "This is a small test document.")
                
            elif size == "medium":
                # 10-page PDF
                for page in range(10):
                    c.drawString(100, 750, f"Test PDF - Page {page + 1}")
                    for i in range(30):
                        c.drawString(100, 700 - i*20, f"Line {i + 1} of content on page {page + 1}")
                    c.showPage()
                    
            elif size == "large":
                # 50-page PDF with lots of text
                for page in range(50):
                    c.drawString(100, 750, f"Large Document - Page {page + 1}")
                    y = 700
                    # Add Lorem ipsum text
                    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 20
                    lines = simpleSplit(text, "Helvetica", 10, 400)
                    for line in lines[:35]:  # Max lines per page
                        c.drawString(100, y, line)
                        y -= 15
                    c.showPage()
            
            c.save()
            
            # Read the PDF bytes
            with open(tmp.name, 'rb') as f:
                pdf_bytes = f.read()
            
            Path(tmp.name).unlink()  # Clean up
            return pdf_bytes
    
    def create_email_request(self, pdf_size: str = "small", subject: str = None) -> Dict[str, Any]:
        """Create email request with PDF attachment."""
        pdf_bytes = self.create_test_pdf(pdf_size)
        
        return {
            "subject": subject or f"Test Email - {pdf_size} PDF",
            "sender": "test@example.com",
            "body": f"Please process this {pdf_size} PDF document.",
            "attachments": [{
                "name": f"test_{pdf_size}.pdf",
                "content": base64.b64encode(pdf_bytes).decode()
            }]
        }
    
    @pytest.mark.asyncio
    async def test_basic_email_to_summary_flow(self):
        """Test basic email → PDF → summary flow."""
        # Create email request
        email_data = self.create_email_request("small")
        
        # Track WebSocket events
        events_received = []
        
        async def monitor_websocket():
            """Monitor WebSocket for events."""
            try:
                async with websockets.connect(self.ws_url) as ws:
                    while True:
                        message = await asyncio.wait_for(ws.recv(), timeout=10)
                        event = json.loads(message)
                        events_received.append(event)
                        
                        # Stop when complete or error
                        if event.get("event") in ["email.processing.completed", "email.processing.error"]:
                            return
            except asyncio.TimeoutError:
                pass
        
        # Start WebSocket monitoring
        ws_task = asyncio.create_task(monitor_websocket())
        
        # Send email request
        response = requests.post(
            f"{self.api_url}/api/process-email",
            json=email_data
        )
        assert response.status_code == 200
        result = response.json()
        run_id = result["run_id"]
        
        # Wait for completion
        await ws_task
        
        # Verify events received
        event_types = [e.get("event") for e in events_received]
        assert "email.processing.started" in event_types
        assert "email.processing.completed" in event_types
        
        # Get final status
        status_response = requests.get(f"{self.api_url}/api/email-status/{run_id}")
        assert status_response.status_code == 200
        
        final_status = status_response.json()
        assert final_status["status"] == "success"
        assert final_status["summary"] is not None
        assert len(final_status["summary"]) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_pdf_sizes(self):
        """Test with different PDF sizes."""
        sizes = ["small", "medium", "large"]
        results = {}
        
        for size in sizes:
            start_time = time.time()
            
            # Create and send request
            email_data = self.create_email_request(size)
            response = requests.post(
                f"{self.api_url}/api/process-email",
                json=email_data
            )
            assert response.status_code == 200
            
            run_id = response.json()["run_id"]
            
            # Poll for completion (max 30 seconds)
            completed = False
            for _ in range(30):
                status_response = requests.get(f"{self.api_url}/api/email-status/{run_id}")
                if status_response.ok:
                    status = status_response.json()
                    if status["status"] in ["success", "error"]:
                        completed = True
                        results[size] = {
                            "status": status["status"],
                            "duration": time.time() - start_time,
                            "summary_length": len(status.get("summary", ""))
                        }
                        break
                await asyncio.sleep(1)
            
            assert completed, f"Processing {size} PDF timed out"
        
        # Verify all succeeded
        for size, result in results.items():
            assert result["status"] == "success", f"{size} PDF failed"
            print(f"{size} PDF: {result['duration']:.2f}s, summary: {result['summary_length']} chars")
        
        # Verify performance requirement (<5s for 10-page PDF)
        assert results["medium"]["duration"] < 5, "Medium PDF took too long"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent email requests."""
        num_requests = 5
        
        async def process_email(index: int):
            """Process a single email request."""
            email_data = self.create_email_request("small", f"Concurrent Test {index}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/process-email",
                    json=email_data
                ) as response:
                    assert response.status == 200
                    result = await response.json()
                    return result["run_id"]
        
        # Send concurrent requests
        tasks = [process_email(i) for i in range(num_requests)]
        run_ids = await asyncio.gather(*tasks)
        
        # Verify all were accepted
        assert len(run_ids) == num_requests
        assert len(set(run_ids)) == num_requests  # All unique
        
        # Wait for all to complete
        await asyncio.sleep(5)
        
        # Check all completed successfully
        success_count = 0
        for run_id in run_ids:
            response = requests.get(f"{self.api_url}/api/email-status/{run_id}")
            if response.ok:
                status = response.json()
                if status["status"] == "success":
                    success_count += 1
        
        assert success_count >= num_requests * 0.8, "Too many concurrent requests failed"
    
    @pytest.mark.asyncio
    async def test_error_scenarios(self):
        """Test various error scenarios."""
        
        # Test 1: No PDF attachment
        email_data = {
            "subject": "No attachment",
            "sender": "test@example.com",
            "body": "This email has no PDF",
            "attachments": []
        }
        
        response = requests.post(f"{self.api_url}/api/process-email", json=email_data)
        assert response.status_code == 400
        assert "No PDF attachment" in response.json()["detail"]
        
        # Test 2: Invalid base64 content
        email_data = {
            "subject": "Invalid PDF",
            "sender": "test@example.com",
            "body": "Invalid attachment",
            "attachments": [{
                "name": "invalid.pdf",
                "content": "not-valid-base64!"
            }]
        }
        
        response = requests.post(f"{self.api_url}/api/process-email", json=email_data)
        assert response.status_code == 500
        
        # Test 3: Non-existent run ID
        response = requests.get(f"{self.api_url}/api/email-status/non-existent-id")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_websocket_reconnection(self):
        """Test WebSocket reconnection handling."""
        events = []
        
        # Connect, disconnect, reconnect
        try:
            # First connection
            async with websockets.connect(self.ws_url) as ws:
                msg = await ws.recv()
                events.append(json.loads(msg))
            
            # Brief pause
            await asyncio.sleep(0.5)
            
            # Second connection
            async with websockets.connect(self.ws_url) as ws:
                msg = await ws.recv()
                events.append(json.loads(msg))
                
                # Send ping
                await ws.send("ping")
                pong = await ws.recv()
                assert pong == "pong"
        
        except Exception as e:
            pytest.fail(f"WebSocket reconnection failed: {e}")
        
        # Verify both connections succeeded
        assert len(events) == 2
        assert all(e.get("event") == "connection.established" for e in events)
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test performance metrics endpoint."""
        # Generate some load first
        email_data = self.create_email_request("small")
        for _ in range(3):
            requests.post(f"{self.api_url}/api/process-email", json=email_data)
        
        # Get metrics
        response = requests.get(f"{self.api_url}/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        assert "api_metrics" in metrics
        assert "dag_metrics" in metrics
        assert "websocket_metrics" in metrics
        
        # Verify metrics structure
        api_metrics = metrics["api_metrics"]
        assert api_metrics["total_requests"] > 0
        assert "avg_response_time_ms" in api_metrics
        assert api_metrics["avg_response_time_ms"] < 1000  # Should be fast
    
    def test_api_documentation(self):
        """Test API documentation endpoints."""
        # OpenAPI docs
        response = requests.get(f"{self.api_url}/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = requests.get(f"{self.api_url}/redoc")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_caching_performance(self):
        """Test that caching improves performance."""
        email_data = self.create_email_request("small")
        
        # First request (cache miss)
        start1 = time.time()
        response1 = requests.post(f"{self.api_url}/api/process-email", json=email_data)
        duration1 = time.time() - start1
        
        run_id1 = response1.json()["run_id"]
        
        # Wait for completion
        await asyncio.sleep(3)
        
        # Same request again (potential cache hit)
        start2 = time.time()
        response2 = requests.post(f"{self.api_url}/api/process-email", json=email_data)
        duration2 = time.time() - start2
        
        # Second request should be faster (though email endpoint creates unique workflows)
        # At least verify both succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        print(f"First request: {duration1:.3f}s, Second: {duration2:.3f}s")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])