#!/usr/bin/env python3
"""
Stress Testing Suite for Multi-Agent Orchestration System.

Advanced stress testing scenarios for concurrent operations,
resource exhaustion, memory leaks, and performance benchmarking.
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
import multiprocessing
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import pytest
import requests
from unittest.mock import patch, MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.e2e.multi_agent_scenarios import E2ETestEnvironment, TestMetrics, Agent, Task


@dataclass
class StressTestResults:
    """Results from stress testing."""
    test_name: str
    start_time: float
    end_time: float
    duration: float
    total_operations: int
    successful_operations: int
    failed_operations: int
    success_rate: float
    throughput: float
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    errors: List[str]
    performance_metrics: Dict[str, Any]


class AdvancedStressTester:
    """Advanced stress testing for orchestration system."""
    
    @pytest.mark.stress
    def test_massive_concurrent_operations(self):
        """Test system with massive concurrent load (500+ operations)."""
        with E2ETestEnvironment("massive_concurrency") as env:
            num_operations = 500
            max_workers = min(50, multiprocessing.cpu_count() * 4)
            
            def stress_operation(operation_id):
                """Single stress operation with timing."""
                start_time = time.time()
                
                task_id = f"MASSIVE_STRESS_{operation_id:04d}"
                agent_id = f"AGENT_{chr(65 + operation_id % 5)}"
                
                task = Task(task_id, f"Massive Stress Task {operation_id}", "LOW", 1, [])
                
                try:
                    # Assign task
                    assign_result = self._assign_task_to_agent(env, agent_id, task)
                    if not assign_result["success"]:
                        return {
                            "success": False, 
                            "phase": "assign", 
                            "error": assign_result["error"],
                            "response_time": time.time() - start_time
                        }
                    
                    # Complete task
                    complete_result = self._complete_task(env, agent_id, task_id)
                    response_time = time.time() - start_time
                    
                    return {
                        "success": complete_result["success"],
                        "phase": "complete" if complete_result["success"] else "complete_failed",
                        "error": complete_result.get("error"),
                        "response_time": response_time
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "phase": "exception",
                        "error": str(e),
                        "response_time": time.time() - start_time
                    }
            
            # Execute massive stress test
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(stress_operation, i)
                    for i in range(num_operations)
                ]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            
            # Analyze results
            stress_results = self._analyze_stress_results(
                "massive_concurrent_operations", start_time, end_time, results
            )
            
            # Assertions for massive stress test
            assert stress_results.success_rate > 0.7  # At least 70% success under massive load
            assert stress_results.throughput > 10      # At least 10 ops/sec
            assert stress_results.avg_response_time < 5.0  # Average under 5 seconds
            
            # Log results
            self._log_stress_results(stress_results)
    
    @pytest.mark.stress
    def test_memory_pressure_operations(self):
        """Test system under memory pressure conditions."""
        with E2ETestEnvironment("memory_pressure") as env:
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Create memory pressure by holding large data structures
            memory_hogs = []
            for i in range(10):
                # Create 10MB chunks to simulate memory pressure
                memory_hogs.append(bytearray(10 * 1024 * 1024))
            
            num_operations = 100
            operations_results = []
            
            def memory_pressure_operation(operation_id):
                """Operation under memory pressure."""
                start_time = time.time()
                
                # Create additional memory pressure during operation
                temp_memory = bytearray(1024 * 1024)  # 1MB temporary allocation
                
                task_id = f"MEM_PRESSURE_{operation_id:03d}"
                agent_id = f"AGENT_{chr(65 + operation_id % 5)}"
                
                task = Task(task_id, f"Memory Pressure Task {operation_id}", "MEDIUM", 1, [])
                
                try:
                    assign_result = self._assign_task_to_agent(env, agent_id, task)
                    if not assign_result["success"]:
                        return {"success": False, "error": "Assignment failed"}
                    
                    complete_result = self._complete_task(env, agent_id, task_id)
                    
                    # Sample memory during operation
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    
                    return {
                        "success": complete_result["success"],
                        "response_time": time.time() - start_time,
                        "memory_usage": current_memory,
                        "error": complete_result.get("error")
                    }
                    
                finally:
                    # Clean up temporary memory
                    del temp_memory
            
            # Execute under memory pressure
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [
                    executor.submit(memory_pressure_operation, i)
                    for i in range(num_operations)
                ]
                results = [future.result() for future in as_completed(futures)]
            
            # Clean up memory pressure
            del memory_hogs
            
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Analyze results
            successful_ops = sum(1 for r in results if r["success"])
            success_rate = successful_ops / num_operations
            avg_memory = sum(r.get("memory_usage", 0) for r in results) / len(results)
            
            # Memory pressure test assertions
            assert success_rate > 0.6  # At least 60% success under memory pressure
            assert final_memory - initial_memory < 200  # Memory growth under 200MB
            
            # Check for excessive memory usage during operations
            max_memory_during_ops = max(r.get("memory_usage", 0) for r in results)
            assert max_memory_during_ops < initial_memory + 500  # No more than 500MB growth
    
    @pytest.mark.stress
    def test_cpu_intensive_operations(self):
        """Test system under CPU-intensive conditions."""
        with E2ETestEnvironment("cpu_intensive") as env:
            
            def cpu_intensive_operation(operation_id):
                """CPU-intensive operation with background load."""
                start_time = time.time()
                
                # Create CPU load
                cpu_work_start = time.time()
                while time.time() - cpu_work_start < 0.1:  # 100ms of CPU work
                    _ = sum(i * i for i in range(1000))
                
                task_id = f"CPU_INTENSIVE_{operation_id:03d}"
                agent_id = f"AGENT_{chr(65 + operation_id % 5)}"
                
                task = Task(task_id, f"CPU Intensive Task {operation_id}", "HIGH", 1, [])
                
                assign_result = self._assign_task_to_agent(env, agent_id, task)
                if not assign_result["success"]:
                    return {"success": False, "error": "Assignment failed"}
                
                complete_result = self._complete_task(env, agent_id, task_id)
                
                return {
                    "success": complete_result["success"],
                    "response_time": time.time() - start_time,
                    "error": complete_result.get("error")
                }
            
            # Create background CPU load
            def background_cpu_load():
                """Background CPU intensive task."""
                end_time = time.time() + 30  # Run for 30 seconds
                while time.time() < end_time:
                    _ = sum(i * i for i in range(10000))
                    time.sleep(0.01)  # Small pause to prevent total system lock
            
            # Start background CPU load
            cpu_thread = threading.Thread(target=background_cpu_load)
            cpu_thread.start()
            
            try:
                # Execute operations under CPU load
                num_operations = 50
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [
                        executor.submit(cpu_intensive_operation, i)
                        for i in range(num_operations)
                    ]
                    results = [future.result() for future in as_completed(futures)]
                
                # Analyze results
                successful_ops = sum(1 for r in results if r["success"])
                success_rate = successful_ops / num_operations
                avg_response_time = sum(r["response_time"] for r in results) / len(results)
                
                # CPU intensive test assertions
                assert success_rate > 0.5  # At least 50% success under CPU load
                assert avg_response_time < 10.0  # Average response under 10 seconds
                
            finally:
                cpu_thread.join(timeout=5)  # Wait for background thread to finish
    
    @pytest.mark.stress
    def test_file_system_stress(self):
        """Test system under file system I/O stress."""
        with E2ETestEnvironment("file_system_stress") as env:
            
            def file_io_operation(operation_id):
                """Operation with intensive file I/O."""
                start_time = time.time()
                
                # Create temporary files to stress file system
                temp_files = []
                try:
                    for i in range(5):
                        temp_file = env.workspace / f"stress_file_{operation_id}_{i}.tmp"
                        with open(temp_file, 'w') as f:
                            f.write("x" * 10000)  # 10KB file
                        temp_files.append(temp_file)
                    
                    task_id = f"FILE_IO_STRESS_{operation_id:03d}"
                    agent_id = f"AGENT_{chr(65 + operation_id % 5)}"
                    
                    task = Task(task_id, f"File I/O Stress Task {operation_id}", "MEDIUM", 1, [])
                    
                    assign_result = self._assign_task_to_agent(env, agent_id, task)
                    if not assign_result["success"]:
                        return {"success": False, "error": "Assignment failed"}
                    
                    complete_result = self._complete_task(env, agent_id, task_id)
                    
                    return {
                        "success": complete_result["success"],
                        "response_time": time.time() - start_time,
                        "error": complete_result.get("error")
                    }
                    
                finally:
                    # Clean up temporary files
                    for temp_file in temp_files:
                        try:
                            temp_file.unlink()
                        except FileNotFoundError:
                            pass
            
            # Execute file I/O stress test
            num_operations = 30
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = [
                    executor.submit(file_io_operation, i)
                    for i in range(num_operations)
                ]
                results = [future.result() for future in as_completed(futures)]
            
            # Analyze results
            successful_ops = sum(1 for r in results if r["success"])
            success_rate = successful_ops / num_operations
            
            # File system stress assertions
            assert success_rate > 0.8  # At least 80% success under file I/O stress
    
    @pytest.mark.stress
    def test_network_latency_simulation(self):
        """Simulate network latency and test system resilience."""
        with E2ETestEnvironment("network_latency") as env:
            
            def latency_operation(operation_id):
                """Operation with simulated network latency."""
                start_time = time.time()
                
                # Simulate network latency
                latency = random.uniform(0.1, 0.5)  # 100-500ms latency
                time.sleep(latency)
                
                task_id = f"LATENCY_TEST_{operation_id:03d}"
                agent_id = f"AGENT_{chr(65 + operation_id % 5)}"
                
                task = Task(task_id, f"Latency Test Task {operation_id}", "MEDIUM", 1, [])
                
                assign_result = self._assign_task_to_agent(env, agent_id, task)
                if not assign_result["success"]:
                    return {"success": False, "error": "Assignment failed", "latency": latency}
                
                complete_result = self._complete_task(env, agent_id, task_id)
                
                return {
                    "success": complete_result["success"],
                    "response_time": time.time() - start_time,
                    "simulated_latency": latency,
                    "error": complete_result.get("error")
                }
            
            # Execute network latency simulation
            num_operations = 40
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(latency_operation, i)
                    for i in range(num_operations)
                ]
                results = [future.result() for future in as_completed(futures)]
            
            # Analyze results
            successful_ops = sum(1 for r in results if r["success"])
            success_rate = successful_ops / num_operations
            avg_latency = sum(r.get("simulated_latency", 0) for r in results) / len(results)
            
            # Network latency test assertions
            assert success_rate > 0.9  # At least 90% success with network latency
            assert avg_latency < 1.0    # Average simulated latency under 1 second
    
    def _assign_task_to_agent(self, env: E2ETestEnvironment, 
                            agent_id: str, task: Task) -> Dict[str, Any]:
        """Assign a task to an agent using the orchestration tools."""
        try:
            result = subprocess.run([
                "bash", str(env.workspace / "tools/assign_task.sh"),
                agent_id, task.task_id, task.title, task.priority, str(task.estimated_hours)
            ], capture_output=True, text=True, cwd=env.workspace, timeout=30)
            
            success = result.returncode == 0
            
            if success:
                task.assigned_agent = agent_id
                env.tasks[task.task_id] = task
                env.agents[agent_id].current_tasks.append(task.task_id)
            
            return {
                "success": success,
                "output": result.stdout,
                "error": result.stderr if not success else None
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Operation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _complete_task(self, env: E2ETestEnvironment, 
                      agent_id: str, task_id: str) -> Dict[str, Any]:
        """Complete a task using the orchestration tools."""
        try:
            result = subprocess.run([
                "bash", str(env.workspace / "tools/complete_task.sh"),
                agent_id, task_id, f"Completed stress test task {task_id}"
            ], capture_output=True, text=True, cwd=env.workspace, timeout=30)
            
            success = result.returncode == 0
            
            if success and task_id in env.tasks:
                env.tasks[task_id].status = "completed"
                env.tasks[task_id].completed_at = datetime.now()
                
                if task_id in env.agents[agent_id].current_tasks:
                    env.agents[agent_id].current_tasks.remove(task_id)
            
            return {
                "success": success,
                "output": result.stdout,
                "error": result.stderr if not success else None
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Operation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_stress_results(self, test_name: str, start_time: float, 
                              end_time: float, results: List[Dict]) -> StressTestResults:
        """Analyze stress test results and create structured output."""
        duration = end_time - start_time
        total_operations = len(results)
        successful_operations = sum(1 for r in results if r.get("success", False))
        failed_operations = total_operations - successful_operations
        success_rate = successful_operations / total_operations if total_operations > 0 else 0
        throughput = total_operations / duration if duration > 0 else 0
        
        # Response time analysis
        response_times = [r.get("response_time", 0) for r in results if "response_time" in r]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # System metrics
        process = psutil.Process()
        memory_usage_mb = process.memory_info().rss / 1024 / 1024
        cpu_usage_percent = process.cpu_percent()
        
        # Collect errors
        errors = [r.get("error", "") for r in results if not r.get("success", False) and r.get("error")]
        
        # Performance metrics
        performance_metrics = {
            "response_time_95th_percentile": self._calculate_percentile(response_times, 95),
            "response_time_99th_percentile": self._calculate_percentile(response_times, 99),
            "error_rate": failed_operations / total_operations if total_operations > 0 else 0,
            "operations_per_second": throughput
        }
        
        return StressTestResults(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            total_operations=total_operations,
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            success_rate=success_rate,
            throughput=throughput,
            avg_response_time=avg_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            errors=errors,
            performance_metrics=performance_metrics
        )
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate the specified percentile of a list of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        
        if index >= len(sorted_values):
            return sorted_values[-1]
        
        return sorted_values[index]
    
    def _log_stress_results(self, results: StressTestResults):
        """Log stress test results to file."""
        results_dict = asdict(results)
        
        # Create results directory if it doesn't exist
        results_dir = PROJECT_ROOT / "tests" / "stress_results"
        results_dir.mkdir(exist_ok=True)
        
        # Write results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"stress_test_{results.test_name}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        # Also log summary to console
        print(f"\n=== Stress Test Results: {results.test_name} ===")
        print(f"Duration: {results.duration:.2f}s")
        print(f"Operations: {results.total_operations}")
        print(f"Success Rate: {results.success_rate:.2%}")
        print(f"Throughput: {results.throughput:.2f} ops/sec")
        print(f"Avg Response Time: {results.avg_response_time:.3f}s")
        print(f"Memory Usage: {results.memory_usage_mb:.1f} MB")
        print(f"CPU Usage: {results.cpu_usage_percent:.1f}%")
        print(f"Results saved to: {results_file}")


if __name__ == "__main__":
    # Run stress tests
    pytest.main([__file__, "-v", "-m", "stress"])