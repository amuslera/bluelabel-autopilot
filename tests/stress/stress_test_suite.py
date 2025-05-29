#!/usr/bin/env python3
"""
Stress Testing Suite for Bluelabel Autopilot
Tests system behavior under high load conditions.
"""

import asyncio
import aiohttp
import time
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import concurrent.futures
import websockets

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.unified_workflow_adapter import UnifiedWorkflowAdapter
from core.agent_registry import register_agent
from agents.ingestion_agent import IngestionAgent
from agents.digest_agent import DigestAgent


class StressTestResults:
    """Container for stress test results."""
    
    def __init__(self):
        self.start_time = time.time()
        self.operations = []
        self.errors = []
        self.response_times = []
        self.success_count = 0
        self.failure_count = 0
        
    def record_operation(self, operation: str, duration: float, success: bool, error: str = None):
        """Record an operation result."""
        self.operations.append({
            "timestamp": time.time(),
            "operation": operation,
            "duration_ms": duration * 1000,
            "success": success,
            "error": error
        })
        
        self.response_times.append(duration * 1000)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            if error:
                self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary statistics."""
        if not self.response_times:
            return {}
        
        total_time = time.time() - self.start_time
        total_ops = len(self.operations)
        
        return {
            "total_duration_seconds": total_time,
            "total_operations": total_ops,
            "operations_per_second": total_ops / total_time if total_time > 0 else 0,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (self.success_count / total_ops * 100) if total_ops > 0 else 0,
            "response_times": {
                "min_ms": min(self.response_times),
                "max_ms": max(self.response_times),
                "avg_ms": sum(self.response_times) / len(self.response_times),
                "p50_ms": sorted(self.response_times)[len(self.response_times) // 2],
                "p95_ms": sorted(self.response_times)[int(len(self.response_times) * 0.95)],
                "p99_ms": sorted(self.response_times)[int(len(self.response_times) * 0.99)]
            },
            "errors": self.errors[:10]  # First 10 errors
        }


class WorkflowStressTester:
    """Stress test workflow execution capabilities."""
    
    def __init__(self):
        self.adapter = None
        self.results = StressTestResults()
        
    async def setup(self):
        """Initialize test environment."""
        # Register agents
        register_agent('ingestion', IngestionAgent)
        register_agent('digest', DigestAgent)
        
        # Initialize adapter
        self.adapter = UnifiedWorkflowAdapter()
        
    async def execute_workflow(self, workflow_id: int) -> Tuple[bool, float, str]:
        """Execute a single workflow and measure performance."""
        start_time = time.time()
        error = None
        success = False
        
        workflow_yaml = f"""
name: stress-test-{workflow_id}
version: 1.0.0
description: Stress test workflow {workflow_id}

steps:
  - name: ingest_data
    agent: ingestion
    input:
      text: "Stress test document {workflow_id}. " * 100  # Moderate size
    output: content

  - name: process_data
    agent: digest
    input:
      content: "{{{{content}}}}"
    output: result
"""
        
        try:
            # Run workflow
            run_id = await self.adapter.run_workflow(
                workflow_name=f"stress-test-{workflow_id}",
                inputs={"workflow_id": workflow_id},
                workflow_yaml=workflow_yaml
            )
            
            # Wait for completion
            timeout = 30  # 30 second timeout
            start_wait = time.time()
            
            while (time.time() - start_wait) < timeout:
                status = self.adapter.get_run_status(run_id)
                if status and status["status"] in ["success", "failed", "cancelled"]:
                    success = status["status"] == "success"
                    if not success:
                        error = status.get("error", "Workflow failed")
                    break
                await asyncio.sleep(0.1)
            else:
                error = "Workflow timeout"
                
        except Exception as e:
            error = str(e)
            
        duration = time.time() - start_time
        return success, duration, error
    
    async def run_concurrent_workflows(self, count: int):
        """Run multiple workflows concurrently."""
        print(f"\n🔥 Running {count} concurrent workflows...")
        
        tasks = []
        for i in range(count):
            task = self.execute_workflow(i)
            tasks.append(task)
            # Small delay to avoid thundering herd
            await asyncio.sleep(0.01)
        
        # Execute all workflows
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Record results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.results.record_operation(
                    f"workflow_{i}",
                    0,
                    False,
                    str(result)
                )
            else:
                success, duration, error = result
                self.results.record_operation(
                    f"workflow_{i}",
                    duration,
                    success,
                    error
                )
    
    async def run_sustained_load(self, workflows_per_second: int, duration_seconds: int):
        """Run sustained load test."""
        print(f"\n🔥 Running sustained load: {workflows_per_second} workflows/sec for {duration_seconds}s...")
        
        start_time = time.time()
        workflow_count = 0
        
        while (time.time() - start_time) < duration_seconds:
            # Start workflows for this second
            batch_start = time.time()
            tasks = []
            
            for _ in range(workflows_per_second):
                task = self.execute_workflow(workflow_count)
                tasks.append(task)
                workflow_count += 1
            
            # Execute batch
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Record results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.results.record_operation(
                        f"sustained_{workflow_count - len(tasks) + i}",
                        0,
                        False,
                        str(result)
                    )
                else:
                    success, duration, error = result
                    self.results.record_operation(
                        f"sustained_{workflow_count - len(tasks) + i}",
                        duration,
                        success,
                        error
                    )
            
            # Wait for next second
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)


class APIStressTester:
    """Stress test API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = StressTestResults()
        
    async def test_api_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: Dict = None):
        """Test a single API endpoint."""
        start_time = time.time()
        success = False
        error = None
        
        try:
            async with session.request(method, f"{self.base_url}{endpoint}", json=data) as response:
                success = response.status < 400
                if not success:
                    error = f"HTTP {response.status}"
        except Exception as e:
            error = str(e)
            
        duration = time.time() - start_time
        self.results.record_operation(endpoint, duration, success, error)
    
    async def run_api_stress_test(self, concurrent_requests: int, total_requests: int):
        """Run API stress test."""
        print(f"\n🔥 Testing API with {concurrent_requests} concurrent requests...")
        
        async with aiohttp.ClientSession() as session:
            # Test endpoints
            endpoints = [
                ("/api/dag-runs", "GET", None),
                ("/health", "GET", None),
                ("/metrics", "GET", None)
            ]
            
            tasks = []
            for i in range(total_requests):
                endpoint, method, data = random.choice(endpoints)
                task = self.test_api_endpoint(session, endpoint, method, data)
                tasks.append(task)
                
                # Limit concurrent requests
                if len(tasks) >= concurrent_requests:
                    await asyncio.gather(*tasks)
                    tasks = []
            
            # Process remaining tasks
            if tasks:
                await asyncio.gather(*tasks)


class WebSocketStressTester:
    """Stress test WebSocket connections."""
    
    def __init__(self, ws_url: str = "ws://localhost:8000/ws"):
        self.ws_url = ws_url
        self.results = StressTestResults()
        
    async def test_websocket_connection(self, client_id: int):
        """Test a single WebSocket connection."""
        start_time = time.time()
        success = False
        error = None
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Send ping
                await websocket.send("ping")
                
                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                success = response == "pong"
                
                # Keep connection alive for a bit
                await asyncio.sleep(random.uniform(1, 3))
                
        except Exception as e:
            error = str(e)
            
        duration = time.time() - start_time
        self.results.record_operation(f"ws_client_{client_id}", duration, success, error)
    
    async def run_websocket_stress_test(self, concurrent_connections: int):
        """Run WebSocket stress test."""
        print(f"\n🔥 Testing WebSocket with {concurrent_connections} concurrent connections...")
        
        tasks = []
        for i in range(concurrent_connections):
            task = self.test_websocket_connection(i)
            tasks.append(task)
            # Small delay to avoid connection storm
            await asyncio.sleep(0.01)
        
        await asyncio.gather(*tasks, return_exceptions=True)


async def run_stress_tests():
    """Run comprehensive stress testing suite."""
    print("🚀 Starting Stress Testing Suite...")
    
    all_results = {}
    
    # 1. Workflow Stress Tests
    print("\n=== WORKFLOW STRESS TESTS ===")
    workflow_tester = WorkflowStressTester()
    await workflow_tester.setup()
    
    # Test different concurrent loads
    for count in [10, 25, 50]:
        await workflow_tester.run_concurrent_workflows(count)
        print(f"✅ Completed {count} concurrent workflows")
    
    # Test sustained load
    await workflow_tester.run_sustained_load(workflows_per_second=5, duration_seconds=10)
    print("✅ Completed sustained load test")
    
    workflow_results = workflow_tester.results.get_summary()
    all_results["workflow_stress_test"] = workflow_results
    
    # 2. API Stress Tests
    print("\n=== API STRESS TESTS ===")
    api_tester = APIStressTester()
    
    try:
        await api_tester.run_api_stress_test(concurrent_requests=50, total_requests=500)
        print("✅ Completed API stress test")
        api_results = api_tester.results.get_summary()
        all_results["api_stress_test"] = api_results
    except Exception as e:
        print(f"⚠️  API stress test failed: {e}")
        all_results["api_stress_test"] = {"error": str(e)}
    
    # 3. WebSocket Stress Tests
    print("\n=== WEBSOCKET STRESS TESTS ===")
    ws_tester = WebSocketStressTester()
    
    try:
        await ws_tester.run_websocket_stress_test(concurrent_connections=100)
        print("✅ Completed WebSocket stress test")
        ws_results = ws_tester.results.get_summary()
        all_results["websocket_stress_test"] = ws_results
    except Exception as e:
        print(f"⚠️  WebSocket stress test failed: {e}")
        all_results["websocket_stress_test"] = {"error": str(e)}
    
    # Save results
    results_path = Path("tests/stress/stress_test_results.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "results": all_results
        }, f, indent=2)
    
    # Print summary
    print("\n📊 STRESS TEST SUMMARY:")
    
    for test_name, results in all_results.items():
        if "error" in results:
            print(f"\n{test_name}: FAILED - {results['error']}")
            continue
            
        print(f"\n{test_name}:")
        print(f"  - Total Operations: {results.get('total_operations', 0)}")
        print(f"  - Success Rate: {results.get('success_rate', 0):.1f}%")
        print(f"  - Ops/Second: {results.get('operations_per_second', 0):.1f}")
        
        if "response_times" in results:
            rt = results["response_times"]
            print(f"  - Response Times:")
            print(f"    - Avg: {rt.get('avg_ms', 0):.1f}ms")
            print(f"    - P95: {rt.get('p95_ms', 0):.1f}ms")
            print(f"    - P99: {rt.get('p99_ms', 0):.1f}ms")
    
    print(f"\n✅ Results saved to {results_path}")
    
    return all_results


if __name__ == "__main__":
    asyncio.run(run_stress_tests())