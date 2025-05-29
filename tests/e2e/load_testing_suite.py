#!/usr/bin/env python3
"""
Load Testing Suite for Dashboard and Monitoring Systems.

Comprehensive load testing for web dashboard, API endpoints,
WebSocket connections, and monitoring infrastructure.
"""

import os
import sys
import time
import json
import asyncio
import random
import threading
import subprocess
import tempfile
import shutil
import psutil
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
import requests
import websockets
import aiohttp
from urllib.parse import urljoin

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class LoadTestMetrics:
    """Metrics from load testing."""
    test_name: str
    start_time: float
    end_time: float
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    requests_per_second: float
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_response_time: float
    min_response_time: float
    concurrent_users: int
    error_types: Dict[str, int]
    response_codes: Dict[str, int]
    throughput_mb_per_sec: float
    memory_usage_mb: float
    cpu_usage_percent: float


@dataclass
class WebSocketMetrics:
    """Metrics specific to WebSocket testing."""
    connections_established: int
    connections_failed: int
    messages_sent: int
    messages_received: int
    avg_message_latency: float
    connection_duration: float
    max_concurrent_connections: int


class LoadTestingSuite:
    """Comprehensive load testing for dashboard and monitoring systems."""
    
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_base_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8000/ws"
        self.results_dir = PROJECT_ROOT / "tests" / "load_test_results"
        self.results_dir.mkdir(exist_ok=True)
    
    @pytest.mark.load
    def test_dashboard_page_load_performance(self):
        """Test dashboard page loading under various user loads."""
        test_scenarios = [
            {"users": 10, "duration": 30, "ramp_up": 5},
            {"users": 25, "duration": 60, "ramp_up": 10},
            {"users": 50, "duration": 90, "ramp_up": 15},
            {"users": 100, "duration": 120, "ramp_up": 20}
        ]
        
        scenario_results = {}
        
        for scenario in test_scenarios:
            print(f"\n--- Load Test: {scenario['users']} users, {scenario['duration']}s ---")
            
            metrics = self._execute_page_load_test(
                users=scenario["users"],
                duration=scenario["duration"],
                ramp_up_time=scenario["ramp_up"]
            )
            
            scenario_results[f"{scenario['users']}_users"] = metrics
            
            print(f"Results: {metrics.success_rate:.1%} success rate, "
                  f"{metrics.requests_per_second:.1f} req/s, "
                  f"P95 latency: {metrics.p95_response_time:.0f}ms")
            
            # Performance assertions for each scenario
            assert metrics.success_rate > 0.95, f"Success rate too low: {metrics.success_rate:.1%}"
            assert metrics.avg_response_time < 3000, f"Average response time too high: {metrics.avg_response_time:.0f}ms"
        
        # Analyze scalability
        self._analyze_load_scalability(scenario_results)
        self._save_load_test_results("dashboard_page_load", scenario_results)
        
        return scenario_results
    
    @pytest.mark.load
    def test_api_endpoint_performance(self):
        """Test API endpoint performance under load."""
        api_endpoints = [
            {"path": "/api/agents/status", "method": "GET"},
            {"path": "/api/tasks/queue", "method": "GET"},
            {"path": "/api/workflows/list", "method": "GET"},
            {"path": "/api/metrics/summary", "method": "GET"},
            {"path": "/api/tasks", "method": "POST", "data": {"title": "Load Test Task", "priority": "MEDIUM"}}
        ]
        
        endpoint_results = {}
        
        for endpoint in api_endpoints:
            endpoint_name = f"{endpoint['method']}_{endpoint['path'].replace('/', '_')}"
            print(f"\n--- API Load Test: {endpoint_name} ---")
            
            metrics = self._execute_api_load_test(
                endpoint=endpoint,
                concurrent_users=50,
                requests_per_user=20,
                duration=60
            )
            
            endpoint_results[endpoint_name] = metrics
            
            print(f"Results: {metrics.success_rate:.1%} success rate, "
                  f"{metrics.requests_per_second:.1f} req/s")
            
            # API performance assertions
            assert metrics.success_rate > 0.98, f"API success rate too low: {metrics.success_rate:.1%}"
            assert metrics.avg_response_time < 1000, f"API response time too high: {metrics.avg_response_time:.0f}ms"
        
        self._save_load_test_results("api_endpoint_performance", endpoint_results)
        return endpoint_results
    
    @pytest.mark.load
    def test_websocket_connection_load(self):
        """Test WebSocket connection performance under load."""
        connection_scenarios = [
            {"concurrent_connections": 50, "messages_per_connection": 100, "duration": 60},
            {"concurrent_connections": 100, "messages_per_connection": 50, "duration": 90},
            {"concurrent_connections": 200, "messages_per_connection": 25, "duration": 120}
        ]
        
        websocket_results = {}
        
        for scenario in connection_scenarios:
            scenario_name = f"{scenario['concurrent_connections']}_connections"
            print(f"\n--- WebSocket Load Test: {scenario_name} ---")
            
            metrics = self._execute_websocket_load_test(
                concurrent_connections=scenario["concurrent_connections"],
                messages_per_connection=scenario["messages_per_connection"],
                duration=scenario["duration"]
            )
            
            websocket_results[scenario_name] = metrics
            
            print(f"Results: {metrics.connections_established} connections, "
                  f"{metrics.messages_received} messages received, "
                  f"{metrics.avg_message_latency:.0f}ms avg latency")
            
            # WebSocket performance assertions
            connection_success_rate = metrics.connections_established / scenario["concurrent_connections"]
            assert connection_success_rate > 0.9, f"WebSocket connection rate too low: {connection_success_rate:.1%}"
            assert metrics.avg_message_latency < 500, f"Message latency too high: {metrics.avg_message_latency:.0f}ms"
        
        self._save_load_test_results("websocket_connection_load", websocket_results)
        return websocket_results
    
    @pytest.mark.load
    def test_mixed_workload_performance(self):
        """Test performance with mixed workload (web + API + WebSocket)."""
        print("\n--- Mixed Workload Load Test ---")
        
        # Configuration for mixed workload
        web_users = 30
        api_users = 40
        websocket_connections = 50
        test_duration = 120
        
        # Start all workload types concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Web dashboard load
            web_future = executor.submit(
                self._execute_page_load_test,
                users=web_users,
                duration=test_duration,
                ramp_up_time=10
            )
            
            # API load
            api_future = executor.submit(
                self._execute_mixed_api_load,
                concurrent_users=api_users,
                duration=test_duration
            )
            
            # WebSocket load
            websocket_future = executor.submit(
                self._execute_websocket_load_test,
                concurrent_connections=websocket_connections,
                messages_per_connection=50,
                duration=test_duration
            )
            
            # Collect results
            web_metrics = web_future.result()
            api_metrics = api_future.result()
            websocket_metrics = websocket_future.result()
        
        mixed_results = {
            "web_load": web_metrics,
            "api_load": api_metrics,
            "websocket_load": websocket_metrics,
            "total_concurrent_users": web_users + api_users + websocket_connections
        }
        
        print(f"Mixed workload results:")
        print(f"Web: {web_metrics.success_rate:.1%} success, {web_metrics.requests_per_second:.1f} req/s")
        print(f"API: {api_metrics.success_rate:.1%} success, {api_metrics.requests_per_second:.1f} req/s")
        print(f"WebSocket: {websocket_metrics.connections_established} connections")
        
        # Mixed workload assertions
        assert web_metrics.success_rate > 0.9, "Web performance degraded in mixed workload"
        assert api_metrics.success_rate > 0.9, "API performance degraded in mixed workload"
        assert websocket_metrics.connections_established > websocket_connections * 0.8, \
            "WebSocket connections degraded in mixed workload"
        
        self._save_load_test_results("mixed_workload_performance", mixed_results)
        return mixed_results
    
    @pytest.mark.load
    def test_sustained_load_endurance(self):
        """Test system endurance under sustained load."""
        print("\n--- Sustained Load Endurance Test ---")
        
        # 30-minute endurance test
        endurance_duration = 1800  # 30 minutes
        steady_users = 25
        
        start_time = time.time()
        metrics_samples = []
        
        # Sample performance every 5 minutes
        sample_interval = 300  # 5 minutes
        next_sample_time = start_time + sample_interval
        
        print(f"Starting {endurance_duration//60}-minute endurance test with {steady_users} users...")
        
        # Start sustained load
        def sustained_load_worker():
            return self._execute_page_load_test(
                users=steady_users,
                duration=endurance_duration,
                ramp_up_time=30
            )
        
        # Monitor system resources during test
        resource_samples = []
        
        def resource_monitor():
            while time.time() - start_time < endurance_duration:
                process = psutil.Process()
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = process.memory_info()
                
                resource_samples.append({
                    "timestamp": time.time() - start_time,
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_info.rss / 1024 / 1024,
                    "memory_percent": process.memory_percent()
                })
                
                time.sleep(30)  # Sample every 30 seconds
        
        # Start monitoring
        resource_thread = threading.Thread(target=resource_monitor)
        resource_thread.start()
        
        try:
            # Execute sustained load
            endurance_metrics = sustained_load_worker()
            
            # Wait for resource monitoring to complete
            resource_thread.join(timeout=10)
            
            # Analyze resource trends
            if resource_samples:
                cpu_values = [s["cpu_percent"] for s in resource_samples]
                memory_values = [s["memory_mb"] for s in resource_samples]
                
                avg_cpu = statistics.mean(cpu_values)
                max_cpu = max(cpu_values)
                memory_growth = memory_values[-1] - memory_values[0] if len(memory_values) > 1 else 0
                
                endurance_analysis = {
                    "duration_minutes": endurance_duration // 60,
                    "steady_users": steady_users,
                    "avg_cpu_percent": avg_cpu,
                    "max_cpu_percent": max_cpu,
                    "memory_growth_mb": memory_growth,
                    "resource_samples": len(resource_samples),
                    "performance_metrics": endurance_metrics
                }
            else:
                endurance_analysis = {
                    "duration_minutes": endurance_duration // 60,
                    "steady_users": steady_users,
                    "performance_metrics": endurance_metrics
                }
            
            print(f"Endurance test completed:")
            print(f"Success rate: {endurance_metrics.success_rate:.1%}")
            print(f"Average CPU: {avg_cpu:.1f}%" if resource_samples else "CPU monitoring unavailable")
            print(f"Memory growth: {memory_growth:.1f}MB" if resource_samples else "Memory monitoring unavailable")
            
            # Endurance test assertions
            assert endurance_metrics.success_rate > 0.95, "Performance degraded during endurance test"
            if resource_samples:
                assert memory_growth < 100, f"Excessive memory growth: {memory_growth:.1f}MB"
                assert avg_cpu < 80, f"CPU usage too high: {avg_cpu:.1f}%"
            
            self._save_load_test_results("sustained_load_endurance", endurance_analysis)
            return endurance_analysis
            
        except Exception as e:
            print(f"Endurance test failed: {e}")
            raise
    
    def _execute_page_load_test(self, users: int, duration: float, ramp_up_time: float) -> LoadTestMetrics:
        """Execute page load test with specified parameters."""
        start_time = time.time()
        end_time = start_time + duration
        
        request_results = []
        active_users = []
        
        def user_session(user_id: int, start_delay: float):
            """Simulate a user session."""
            time.sleep(start_delay)
            session_end = time.time() + duration - start_delay
            
            with requests.Session() as session:
                while time.time() < session_end:
                    req_start = time.time()
                    
                    try:
                        response = session.get(self.base_url, timeout=30)
                        req_end = time.time()
                        
                        request_results.append({
                            "user_id": user_id,
                            "success": response.status_code == 200,
                            "status_code": response.status_code,
                            "response_time": (req_end - req_start) * 1000,  # ms
                            "response_size": len(response.content),
                            "timestamp": req_end - start_time
                        })
                        
                    except Exception as e:
                        req_end = time.time()
                        request_results.append({
                            "user_id": user_id,
                            "success": False,
                            "status_code": 0,
                            "response_time": (req_end - req_start) * 1000,
                            "response_size": 0,
                            "timestamp": req_end - start_time,
                            "error": str(e)
                        })
                    
                    # Wait between requests (simulate user think time)
                    time.sleep(random.uniform(2, 5))
        
        # Start users with ramp-up
        with ThreadPoolExecutor(max_workers=users) as executor:
            for user_id in range(users):
                start_delay = (user_id / users) * ramp_up_time
                executor.submit(user_session, user_id, start_delay)
        
        # Wait for all users to complete
        time.sleep(max(0, duration - (time.time() - start_time)))
        
        # Calculate metrics
        return self._calculate_load_metrics("page_load_test", start_time, request_results, users)
    
    def _execute_api_load_test(self, endpoint: Dict, concurrent_users: int, 
                              requests_per_user: int, duration: float) -> LoadTestMetrics:
        """Execute API load test."""
        start_time = time.time()
        request_results = []
        
        def api_user_session(user_id: int):
            """Simulate API user session."""
            with requests.Session() as session:
                for req_num in range(requests_per_user):
                    req_start = time.time()
                    
                    try:
                        url = urljoin(self.api_base_url, endpoint["path"])
                        
                        if endpoint["method"] == "GET":
                            response = session.get(url, timeout=10)
                        elif endpoint["method"] == "POST":
                            response = session.post(url, json=endpoint.get("data", {}), timeout=10)
                        else:
                            response = session.request(endpoint["method"], url, timeout=10)
                        
                        req_end = time.time()
                        
                        request_results.append({
                            "user_id": user_id,
                            "request_num": req_num,
                            "success": 200 <= response.status_code < 300,
                            "status_code": response.status_code,
                            "response_time": (req_end - req_start) * 1000,
                            "response_size": len(response.content),
                            "timestamp": req_end - start_time
                        })
                        
                    except Exception as e:
                        req_end = time.time()
                        request_results.append({
                            "user_id": user_id,
                            "request_num": req_num,
                            "success": False,
                            "status_code": 0,
                            "response_time": (req_end - req_start) * 1000,
                            "response_size": 0,
                            "timestamp": req_end - start_time,
                            "error": str(e)
                        })
                    
                    # Small delay between requests
                    time.sleep(0.1)
        
        # Execute concurrent API requests
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(api_user_session, user_id) for user_id in range(concurrent_users)]
            
            # Wait for all requests to complete
            for future in as_completed(futures):
                future.result()
        
        return self._calculate_load_metrics("api_load_test", start_time, request_results, concurrent_users)
    
    def _execute_websocket_load_test(self, concurrent_connections: int, 
                                   messages_per_connection: int, duration: float) -> WebSocketMetrics:
        """Execute WebSocket load test."""
        start_time = time.time()
        
        connections_established = 0
        connections_failed = 0
        messages_sent = 0
        messages_received = 0
        message_latencies = []
        
        async def websocket_client(client_id: int):
            """Single WebSocket client."""
            nonlocal connections_established, connections_failed, messages_sent, messages_received
            
            try:
                async with websockets.connect(self.websocket_url) as websocket:
                    connections_established += 1
                    
                    # Send messages
                    for msg_num in range(messages_per_connection):
                        msg_start = time.time()
                        message = {
                            "client_id": client_id,
                            "message_num": msg_num,
                            "timestamp": msg_start,
                            "data": f"Load test message {msg_num} from client {client_id}"
                        }
                        
                        await websocket.send(json.dumps(message))
                        messages_sent += 1
                        
                        # Wait for response
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            msg_end = time.time()
                            
                            messages_received += 1
                            message_latencies.append((msg_end - msg_start) * 1000)  # ms
                            
                        except asyncio.TimeoutError:
                            pass
                        
                        # Small delay between messages
                        await asyncio.sleep(0.1)
                    
                    # Keep connection alive for duration
                    await asyncio.sleep(max(0, duration - (time.time() - start_time)))
                    
            except Exception as e:
                connections_failed += 1
        
        async def run_websocket_load_test():
            """Run the WebSocket load test."""
            tasks = [websocket_client(i) for i in range(concurrent_connections)]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Execute WebSocket load test
        asyncio.run(run_websocket_load_test())
        
        avg_message_latency = statistics.mean(message_latencies) if message_latencies else 0
        connection_duration = time.time() - start_time
        
        return WebSocketMetrics(
            connections_established=connections_established,
            connections_failed=connections_failed,
            messages_sent=messages_sent,
            messages_received=messages_received,
            avg_message_latency=avg_message_latency,
            connection_duration=connection_duration,
            max_concurrent_connections=concurrent_connections
        )
    
    def _execute_mixed_api_load(self, concurrent_users: int, duration: float) -> LoadTestMetrics:
        """Execute mixed API endpoint load test."""
        api_endpoints = [
            {"path": "/api/agents/status", "method": "GET", "weight": 3},
            {"path": "/api/tasks/queue", "method": "GET", "weight": 2},
            {"path": "/api/workflows/list", "method": "GET", "weight": 1},
            {"path": "/api/metrics/summary", "method": "GET", "weight": 2}
        ]
        
        # Create weighted endpoint list
        weighted_endpoints = []
        for endpoint in api_endpoints:
            weighted_endpoints.extend([endpoint] * endpoint["weight"])
        
        start_time = time.time()
        end_time = start_time + duration
        request_results = []
        
        def mixed_api_user(user_id: int):
            """User making mixed API requests."""
            with requests.Session() as session:
                while time.time() < end_time:
                    endpoint = random.choice(weighted_endpoints)
                    req_start = time.time()
                    
                    try:
                        url = urljoin(self.api_base_url, endpoint["path"])
                        response = session.get(url, timeout=10)
                        req_end = time.time()
                        
                        request_results.append({
                            "user_id": user_id,
                            "endpoint": endpoint["path"],
                            "success": 200 <= response.status_code < 300,
                            "status_code": response.status_code,
                            "response_time": (req_end - req_start) * 1000,
                            "response_size": len(response.content),
                            "timestamp": req_end - start_time
                        })
                        
                    except Exception as e:
                        req_end = time.time()
                        request_results.append({
                            "user_id": user_id,
                            "endpoint": endpoint["path"],
                            "success": False,
                            "status_code": 0,
                            "response_time": (req_end - req_start) * 1000,
                            "response_size": 0,
                            "timestamp": req_end - start_time,
                            "error": str(e)
                        })
                    
                    # Random delay between requests
                    time.sleep(random.uniform(0.5, 2.0))
        
        # Execute mixed API load
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(mixed_api_user, user_id) for user_id in range(concurrent_users)]
            
            for future in as_completed(futures):
                future.result()
        
        return self._calculate_load_metrics("mixed_api_load", start_time, request_results, concurrent_users)
    
    def _calculate_load_metrics(self, test_name: str, start_time: float, 
                               request_results: List[Dict], concurrent_users: int) -> LoadTestMetrics:
        """Calculate load test metrics from request results."""
        end_time = time.time()
        duration = end_time - start_time
        
        if not request_results:
            return LoadTestMetrics(
                test_name=test_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                success_rate=0.0,
                requests_per_second=0.0,
                avg_response_time=0.0,
                p50_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                max_response_time=0.0,
                min_response_time=0.0,
                concurrent_users=concurrent_users,
                error_types={},
                response_codes={},
                throughput_mb_per_sec=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0
            )
        
        # Basic metrics
        total_requests = len(request_results)
        successful_requests = sum(1 for r in request_results if r["success"])
        failed_requests = total_requests - successful_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        # Response time metrics
        response_times = [r["response_time"] for r in request_results]
        avg_response_time = statistics.mean(response_times)
        p50_response_time = statistics.median(response_times)
        
        sorted_times = sorted(response_times)
        p95_index = int(0.95 * len(sorted_times))
        p99_index = int(0.99 * len(sorted_times))
        
        p95_response_time = sorted_times[p95_index] if sorted_times else 0
        p99_response_time = sorted_times[p99_index] if sorted_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Throughput metrics
        requests_per_second = total_requests / duration if duration > 0 else 0
        
        # Data transfer metrics
        total_bytes = sum(r.get("response_size", 0) for r in request_results)
        throughput_mb_per_sec = (total_bytes / 1024 / 1024) / duration if duration > 0 else 0
        
        # Error analysis
        error_types = {}
        response_codes = {}
        
        for result in request_results:
            # Count response codes
            code = str(result.get("status_code", "unknown"))
            response_codes[code] = response_codes.get(code, 0) + 1
            
            # Count error types
            if not result["success"] and "error" in result:
                error_type = type(result["error"]).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # System resource usage
        process = psutil.Process()
        memory_usage_mb = process.memory_info().rss / 1024 / 1024
        cpu_usage_percent = process.cpu_percent()
        
        return LoadTestMetrics(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            success_rate=success_rate,
            requests_per_second=requests_per_second,
            avg_response_time=avg_response_time,
            p50_response_time=p50_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            concurrent_users=concurrent_users,
            error_types=error_types,
            response_codes=response_codes,
            throughput_mb_per_sec=throughput_mb_per_sec,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent
        )
    
    def _analyze_load_scalability(self, scenario_results: Dict[str, LoadTestMetrics]):
        """Analyze load scalability across different user counts."""
        print("\n=== Load Scalability Analysis ===")
        
        user_counts = []
        throughputs = []
        response_times = []
        
        for scenario_name, metrics in scenario_results.items():
            users = int(scenario_name.split("_")[0])
            user_counts.append(users)
            throughputs.append(metrics.requests_per_second)
            response_times.append(metrics.avg_response_time)
        
        # Sort by user count
        sorted_data = sorted(zip(user_counts, throughputs, response_times))
        
        for users, throughput, response_time in sorted_data:
            print(f"Users {users:3d}: {throughput:6.1f} req/s, {response_time:6.0f}ms avg")
        
        # Calculate efficiency metrics
        if len(sorted_data) > 1:
            base_users, base_throughput, base_response = sorted_data[0]
            max_users, max_throughput, max_response = sorted_data[-1]
            
            throughput_scaling = max_throughput / base_throughput
            user_scaling = max_users / base_users
            efficiency = throughput_scaling / user_scaling
            
            print(f"\nScaling efficiency: {efficiency:.2f}")
            print(f"Response time degradation: {max_response / base_response:.2f}x")
    
    def _save_load_test_results(self, test_name: str, results: Dict):
        """Save load test results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"{test_name}_{timestamp}.json"
        
        # Convert dataclasses to dictionaries
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, (LoadTestMetrics, WebSocketMetrics)):
                serializable_results[key] = asdict(value)
            else:
                serializable_results[key] = value
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"Load test results saved to: {results_file}")


if __name__ == "__main__":
    # Run load tests
    suite = LoadTestingSuite()
    
    # Run individual test methods
    print("Starting Load Testing Suite...")
    
    try:
        suite.test_dashboard_page_load_performance()
        suite.test_api_endpoint_performance()
        suite.test_websocket_connection_load()
        suite.test_mixed_workload_performance()
        # suite.test_sustained_load_endurance()  # Uncomment for full endurance test
        
        print("\nAll load tests completed successfully!")
        
    except Exception as e:
        print(f"Load test failed: {e}")
        raise