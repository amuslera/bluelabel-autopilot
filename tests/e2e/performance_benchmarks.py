#!/usr/bin/env python3
"""
Performance Benchmarking Suite for Multi-Agent Orchestration System.

Comprehensive performance benchmarks for large-scale operations,
throughput analysis, latency measurements, and scalability testing.
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
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
import requests
from collections import defaultdict
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.e2e.multi_agent_scenarios import E2ETestEnvironment, TestMetrics, Agent, Task


@dataclass
class BenchmarkMetrics:
    """Comprehensive benchmark metrics."""
    benchmark_name: str
    start_time: float
    end_time: float
    total_duration: float
    
    # Operation metrics
    total_operations: int
    successful_operations: int
    failed_operations: int
    success_rate: float
    
    # Performance metrics
    throughput_ops_per_sec: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    max_latency_ms: float
    min_latency_ms: float
    
    # Resource metrics
    peak_memory_mb: float
    avg_memory_mb: float
    peak_cpu_percent: float
    avg_cpu_percent: float
    
    # Scalability metrics
    agents_utilized: int
    concurrent_operations: int
    queue_depth_max: int
    
    # Additional metrics
    errors: List[str] = field(default_factory=list)
    detailed_timings: Dict[str, List[float]] = field(default_factory=dict)
    resource_samples: List[Dict[str, float]] = field(default_factory=list)


class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmarking for orchestration system."""
    
    @pytest.mark.benchmark
    def test_large_scale_throughput(self):
        """Benchmark throughput with large number of operations."""
        with E2ETestEnvironment("large_scale_throughput") as env:
            # Test different scale levels
            scale_levels = [100, 500, 1000, 2000]
            
            results = {}
            
            for scale in scale_levels:
                print(f"\n--- Testing scale: {scale} operations ---")
                
                # Generate tasks
                tasks = self._generate_benchmark_tasks(scale)
                
                # Start resource monitoring
                resource_monitor = ResourceMonitor()
                resource_monitor.start()
                
                start_time = time.time()
                latencies = []
                
                try:
                    # Execute operations with measured latency
                    with ThreadPoolExecutor(max_workers=min(50, scale // 10)) as executor:
                        def execute_operation(task):
                            op_start = time.time()
                            
                            agent_id = f"AGENT_{chr(65 + hash(task.task_id) % 5)}"
                            
                            # Assign task
                            assign_result = self._assign_task_to_agent(env, agent_id, task)
                            if not assign_result["success"]:
                                return {"success": False, "latency": time.time() - op_start}
                            
                            # Complete task
                            complete_result = self._complete_task(env, agent_id, task.task_id)
                            
                            latency = (time.time() - op_start) * 1000  # Convert to ms
                            return {
                                "success": complete_result["success"],
                                "latency": latency
                            }
                        
                        futures = [executor.submit(execute_operation, task) for task in tasks]
                        operation_results = [future.result() for future in as_completed(futures)]
                
                finally:
                    resource_monitor.stop()
                
                end_time = time.time()
                
                # Analyze results
                successful_ops = sum(1 for r in operation_results if r["success"])
                latencies = [r["latency"] for r in operation_results if r["success"]]
                
                metrics = BenchmarkMetrics(
                    benchmark_name=f"throughput_scale_{scale}",
                    start_time=start_time,
                    end_time=end_time,
                    total_duration=end_time - start_time,
                    total_operations=scale,
                    successful_operations=successful_ops,
                    failed_operations=scale - successful_ops,
                    success_rate=successful_ops / scale,
                    throughput_ops_per_sec=successful_ops / (end_time - start_time),
                    avg_latency_ms=statistics.mean(latencies) if latencies else 0,
                    p50_latency_ms=statistics.median(latencies) if latencies else 0,
                    p95_latency_ms=np.percentile(latencies, 95) if latencies else 0,
                    p99_latency_ms=np.percentile(latencies, 99) if latencies else 0,
                    max_latency_ms=max(latencies) if latencies else 0,
                    min_latency_ms=min(latencies) if latencies else 0,
                    peak_memory_mb=resource_monitor.peak_memory_mb,
                    avg_memory_mb=resource_monitor.avg_memory_mb,
                    peak_cpu_percent=resource_monitor.peak_cpu_percent,
                    avg_cpu_percent=resource_monitor.avg_cpu_percent,
                    agents_utilized=5,  # Fixed number of agents in test
                    concurrent_operations=min(50, scale // 10),
                    queue_depth_max=scale,
                    detailed_timings={"operation_latencies": latencies},
                    resource_samples=resource_monitor.samples
                )
                
                results[scale] = metrics
                
                # Log intermediate results
                print(f"Scale {scale}: {metrics.throughput_ops_per_sec:.1f} ops/sec, "
                      f"P95 latency: {metrics.p95_latency_ms:.1f}ms")
                
                # Performance assertions for each scale
                assert metrics.success_rate > 0.8, f"Scale {scale}: Success rate too low"
                assert metrics.throughput_ops_per_sec > 5, f"Scale {scale}: Throughput too low"
            
            # Analyze scalability trends
            self._analyze_scalability_trends(results)
            
            # Save comprehensive results
            self._save_benchmark_results("large_scale_throughput", results)
    
    @pytest.mark.benchmark
    def test_concurrent_agent_performance(self):
        """Benchmark performance with varying numbers of concurrent agents."""
        with E2ETestEnvironment("concurrent_agent_performance") as env:
            # Test different concurrent agent counts
            agent_counts = [1, 3, 5, 8, 10]
            num_tasks_per_test = 200
            
            results = {}
            
            for agent_count in agent_counts:
                print(f"\n--- Testing with {agent_count} concurrent agents ---")
                
                # Limit agents for this test
                active_agents = list(env.agents.keys())[:agent_count]
                
                tasks = self._generate_benchmark_tasks(num_tasks_per_test)
                
                resource_monitor = ResourceMonitor()
                resource_monitor.start()
                
                start_time = time.time()
                
                try:
                    # Distribute tasks across available agents
                    agent_task_queues = defaultdict(list)
                    for i, task in enumerate(tasks):
                        agent_id = active_agents[i % len(active_agents)]
                        agent_task_queues[agent_id].append(task)
                    
                    # Execute tasks per agent concurrently
                    def execute_agent_queue(agent_id, agent_tasks):
                        """Execute all tasks for a specific agent."""
                        agent_results = []
                        for task in agent_tasks:
                            op_start = time.time()
                            
                            assign_result = self._assign_task_to_agent(env, agent_id, task)
                            if assign_result["success"]:
                                complete_result = self._complete_task(env, agent_id, task.task_id)
                                success = complete_result["success"]
                            else:
                                success = False
                            
                            latency = (time.time() - op_start) * 1000
                            agent_results.append({"success": success, "latency": latency})
                        
                        return agent_results
                    
                    # Run agent queues concurrently
                    with ThreadPoolExecutor(max_workers=agent_count) as executor:
                        agent_futures = {
                            executor.submit(execute_agent_queue, agent_id, tasks): agent_id
                            for agent_id, tasks in agent_task_queues.items()
                        }
                        
                        all_results = []
                        for future in as_completed(agent_futures):
                            agent_results = future.result()
                            all_results.extend(agent_results)
                
                finally:
                    resource_monitor.stop()
                
                end_time = time.time()
                
                # Analyze results
                successful_ops = sum(1 for r in all_results if r["success"])
                latencies = [r["latency"] for r in all_results if r["success"]]
                
                metrics = BenchmarkMetrics(
                    benchmark_name=f"concurrent_agents_{agent_count}",
                    start_time=start_time,
                    end_time=end_time,
                    total_duration=end_time - start_time,
                    total_operations=num_tasks_per_test,
                    successful_operations=successful_ops,
                    failed_operations=num_tasks_per_test - successful_ops,
                    success_rate=successful_ops / num_tasks_per_test,
                    throughput_ops_per_sec=successful_ops / (end_time - start_time),
                    avg_latency_ms=statistics.mean(latencies) if latencies else 0,
                    p50_latency_ms=statistics.median(latencies) if latencies else 0,
                    p95_latency_ms=np.percentile(latencies, 95) if latencies else 0,
                    p99_latency_ms=np.percentile(latencies, 99) if latencies else 0,
                    max_latency_ms=max(latencies) if latencies else 0,
                    min_latency_ms=min(latencies) if latencies else 0,
                    peak_memory_mb=resource_monitor.peak_memory_mb,
                    avg_memory_mb=resource_monitor.avg_memory_mb,
                    peak_cpu_percent=resource_monitor.peak_cpu_percent,
                    avg_cpu_percent=resource_monitor.avg_cpu_percent,
                    agents_utilized=agent_count,
                    concurrent_operations=agent_count,
                    queue_depth_max=max(len(tasks) for tasks in agent_task_queues.values()),
                    detailed_timings={"operation_latencies": latencies},
                    resource_samples=resource_monitor.samples
                )
                
                results[agent_count] = metrics
                
                print(f"Agents {agent_count}: {metrics.throughput_ops_per_sec:.1f} ops/sec")
            
            # Analyze concurrent agent performance
            self._analyze_concurrency_performance(results)
            self._save_benchmark_results("concurrent_agent_performance", results)
    
    @pytest.mark.benchmark
    def test_memory_scaling_performance(self):
        """Benchmark memory usage scaling with operation count."""
        with E2ETestEnvironment("memory_scaling") as env:
            operation_counts = [50, 100, 250, 500, 1000]
            
            results = {}
            
            for op_count in operation_counts:
                print(f"\n--- Testing memory scaling with {op_count} operations ---")
                
                # Measure initial memory
                initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                tasks = self._generate_benchmark_tasks(op_count)
                
                memory_samples = []
                start_time = time.time()
                
                # Monitor memory during operations
                def memory_monitor():
                    while getattr(memory_monitor, 'running', True):
                        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                        memory_samples.append({
                            'timestamp': time.time() - start_time,
                            'memory_mb': memory_mb
                        })
                        time.sleep(0.1)
                
                memory_monitor.running = True
                monitor_thread = threading.Thread(target=memory_monitor)
                monitor_thread.start()
                
                try:
                    # Execute operations
                    successful_ops = 0
                    for i, task in enumerate(tasks):
                        agent_id = f"AGENT_{chr(65 + i % 5)}"
                        
                        assign_result = self._assign_task_to_agent(env, agent_id, task)
                        if assign_result["success"]:
                            complete_result = self._complete_task(env, agent_id, task.task_id)
                            if complete_result["success"]:
                                successful_ops += 1
                        
                        # Sample memory every 10 operations
                        if i % 10 == 0:
                            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                            memory_samples.append({
                                'operation': i,
                                'memory_mb': current_memory
                            })
                
                finally:
                    memory_monitor.running = False
                    monitor_thread.join(timeout=1)
                
                end_time = time.time()
                final_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                # Analyze memory usage
                memory_values = [s['memory_mb'] for s in memory_samples if 'memory_mb' in s]
                peak_memory = max(memory_values) if memory_values else final_memory
                avg_memory = statistics.mean(memory_values) if memory_values else final_memory
                memory_growth = final_memory - initial_memory
                
                metrics = BenchmarkMetrics(
                    benchmark_name=f"memory_scaling_{op_count}",
                    start_time=start_time,
                    end_time=end_time,
                    total_duration=end_time - start_time,
                    total_operations=op_count,
                    successful_operations=successful_ops,
                    failed_operations=op_count - successful_ops,
                    success_rate=successful_ops / op_count,
                    throughput_ops_per_sec=successful_ops / (end_time - start_time),
                    avg_latency_ms=0,  # Not measured in this test
                    p50_latency_ms=0,
                    p95_latency_ms=0,
                    p99_latency_ms=0,
                    max_latency_ms=0,
                    min_latency_ms=0,
                    peak_memory_mb=peak_memory,
                    avg_memory_mb=avg_memory,
                    peak_cpu_percent=0,  # Not the focus of this test
                    avg_cpu_percent=0,
                    agents_utilized=5,
                    concurrent_operations=1,  # Sequential for memory testing
                    queue_depth_max=op_count,
                    detailed_timings={"memory_growth": memory_growth},
                    resource_samples=memory_samples
                )
                
                results[op_count] = metrics
                
                print(f"Operations {op_count}: Peak memory {peak_memory:.1f}MB, "
                      f"Growth {memory_growth:.1f}MB")
                
                # Memory scaling assertions
                assert memory_growth < op_count * 0.1, f"Excessive memory growth: {memory_growth:.1f}MB"
            
            # Analyze memory scaling trends
            self._analyze_memory_scaling(results)
            self._save_benchmark_results("memory_scaling_performance", results)
    
    @pytest.mark.benchmark
    def test_sustained_load_performance(self):
        """Benchmark sustained load performance over extended period."""
        with E2ETestEnvironment("sustained_load") as env:
            duration_minutes = 5  # 5 minute sustained test
            operations_per_minute = 60  # 1 operation per second
            
            print(f"\n--- Sustained load test: {duration_minutes} minutes ---")
            
            resource_monitor = ResourceMonitor(sample_interval=1.0)
            resource_monitor.start()
            
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            operation_results = []
            operation_count = 0
            
            try:
                while time.time() < end_time:
                    minute_start = time.time()
                    
                    # Execute operations for this minute
                    for _ in range(operations_per_minute):
                        if time.time() >= end_time:
                            break
                        
                        operation_count += 1
                        task = Task(
                            f"SUSTAINED_LOAD_{operation_count:04d}",
                            f"Sustained Load Task {operation_count}",
                            "MEDIUM",
                            1,
                            []
                        )
                        
                        op_start = time.time()
                        agent_id = f"AGENT_{chr(65 + operation_count % 5)}"
                        
                        assign_result = self._assign_task_to_agent(env, agent_id, task)
                        if assign_result["success"]:
                            complete_result = self._complete_task(env, agent_id, task.task_id)
                            success = complete_result["success"]
                        else:
                            success = False
                        
                        latency = (time.time() - op_start) * 1000
                        operation_results.append({
                            "success": success,
                            "latency": latency,
                            "timestamp": time.time() - start_time
                        })
                        
                        # Maintain target rate
                        elapsed = time.time() - minute_start
                        expected_elapsed = len([r for r in operation_results 
                                             if r["timestamp"] >= elapsed - 60]) / operations_per_minute * 60
                        if elapsed < expected_elapsed:
                            time.sleep(expected_elapsed - elapsed)
            
            finally:
                resource_monitor.stop()
            
            actual_end_time = time.time()
            actual_duration = actual_end_time - start_time
            
            # Analyze sustained load results
            successful_ops = sum(1 for r in operation_results if r["success"])
            latencies = [r["latency"] for r in operation_results if r["success"]]
            
            # Calculate performance degradation over time
            time_windows = self._analyze_performance_over_time(operation_results, start_time)
            
            metrics = BenchmarkMetrics(
                benchmark_name="sustained_load",
                start_time=start_time,
                end_time=actual_end_time,
                total_duration=actual_duration,
                total_operations=operation_count,
                successful_operations=successful_ops,
                failed_operations=operation_count - successful_ops,
                success_rate=successful_ops / operation_count if operation_count > 0 else 0,
                throughput_ops_per_sec=successful_ops / actual_duration,
                avg_latency_ms=statistics.mean(latencies) if latencies else 0,
                p50_latency_ms=statistics.median(latencies) if latencies else 0,
                p95_latency_ms=np.percentile(latencies, 95) if latencies else 0,
                p99_latency_ms=np.percentile(latencies, 99) if latencies else 0,
                max_latency_ms=max(latencies) if latencies else 0,
                min_latency_ms=min(latencies) if latencies else 0,
                peak_memory_mb=resource_monitor.peak_memory_mb,
                avg_memory_mb=resource_monitor.avg_memory_mb,
                peak_cpu_percent=resource_monitor.peak_cpu_percent,
                avg_cpu_percent=resource_monitor.avg_cpu_percent,
                agents_utilized=5,
                concurrent_operations=1,
                queue_depth_max=operation_count,
                detailed_timings={"time_windows": time_windows},
                resource_samples=resource_monitor.samples
            )
            
            print(f"Sustained load completed: {metrics.throughput_ops_per_sec:.1f} avg ops/sec")
            
            # Sustained load assertions
            assert metrics.success_rate > 0.95, "Sustained load success rate too low"
            assert metrics.avg_latency_ms < 1000, "Average latency too high during sustained load"
            
            self._save_benchmark_results("sustained_load_performance", {"sustained": metrics})
    
    def _generate_benchmark_tasks(self, count: int) -> List[Task]:
        """Generate tasks for benchmarking."""
        tasks = []
        for i in range(count):
            task = Task(
                task_id=f"BENCHMARK_TASK_{i:05d}",
                title=f"Benchmark Task {i}",
                priority=random.choice(["HIGH", "MEDIUM", "LOW"]),
                estimated_hours=1,
                dependencies=[],
                created_at=datetime.now()
            )
            tasks.append(task)
        return tasks
    
    def _assign_task_to_agent(self, env: E2ETestEnvironment, 
                            agent_id: str, task: Task) -> Dict[str, Any]:
        """Assign a task to an agent."""
        try:
            result = subprocess.run([
                "bash", str(env.workspace / "tools/assign_task.sh"),
                agent_id, task.task_id, task.title, task.priority, str(task.estimated_hours)
            ], capture_output=True, text=True, cwd=env.workspace, timeout=10)
            
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
            return {"success": False, "error": "Assignment timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _complete_task(self, env: E2ETestEnvironment, 
                      agent_id: str, task_id: str) -> Dict[str, Any]:
        """Complete a task."""
        try:
            result = subprocess.run([
                "bash", str(env.workspace / "tools/complete_task.sh"),
                agent_id, task_id, f"Completed benchmark task {task_id}"
            ], capture_output=True, text=True, cwd=env.workspace, timeout=10)
            
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
            return {"success": False, "error": "Completion timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_scalability_trends(self, results: Dict[int, BenchmarkMetrics]):
        """Analyze scalability trends across different scales."""
        scales = sorted(results.keys())
        throughputs = [results[scale].throughput_ops_per_sec for scale in scales]
        latencies = [results[scale].p95_latency_ms for scale in scales]
        
        print("\n=== Scalability Analysis ===")
        for i, scale in enumerate(scales):
            print(f"Scale {scale:4d}: {throughputs[i]:6.1f} ops/sec, "
                  f"P95 latency: {latencies[i]:6.1f}ms")
        
        # Check for performance degradation
        if len(throughputs) > 1:
            throughput_ratio = throughputs[-1] / throughputs[0]
            scale_ratio = scales[-1] / scales[0]
            efficiency = throughput_ratio / scale_ratio
            
            print(f"\nScalability efficiency: {efficiency:.2f}")
            print(f"(1.0 = linear scaling, >1.0 = super-linear, <1.0 = sub-linear)")
    
    def _analyze_concurrency_performance(self, results: Dict[int, BenchmarkMetrics]):
        """Analyze performance vs concurrent agent count."""
        agent_counts = sorted(results.keys())
        
        print("\n=== Concurrency Analysis ===")
        for count in agent_counts:
            metrics = results[count]
            print(f"Agents {count}: {metrics.throughput_ops_per_sec:.1f} ops/sec, "
                  f"Avg latency: {metrics.avg_latency_ms:.1f}ms")
    
    def _analyze_memory_scaling(self, results: Dict[int, BenchmarkMetrics]):
        """Analyze memory usage scaling."""
        op_counts = sorted(results.keys())
        
        print("\n=== Memory Scaling Analysis ===")
        for count in op_counts:
            metrics = results[count]
            memory_per_op = metrics.peak_memory_mb / count
            print(f"Operations {count:4d}: {metrics.peak_memory_mb:.1f}MB peak, "
                  f"{memory_per_op:.3f}MB/op")
    
    def _analyze_performance_over_time(self, operation_results: List[Dict], 
                                     start_time: float) -> List[Dict]:
        """Analyze performance degradation over time."""
        # Group results into time windows (e.g., 30-second windows)
        window_size = 30  # seconds
        windows = defaultdict(list)
        
        for result in operation_results:
            window = int(result["timestamp"] // window_size)
            windows[window].append(result)
        
        window_analysis = []
        for window_num in sorted(windows.keys()):
            window_results = windows[window_num]
            successful = [r for r in window_results if r["success"]]
            
            if successful:
                avg_latency = statistics.mean([r["latency"] for r in successful])
                success_rate = len(successful) / len(window_results)
                throughput = len(successful) / window_size
                
                window_analysis.append({
                    "window": window_num,
                    "start_time": window_num * window_size,
                    "success_rate": success_rate,
                    "avg_latency_ms": avg_latency,
                    "throughput_ops_per_sec": throughput
                })
        
        return window_analysis
    
    def _save_benchmark_results(self, benchmark_name: str, results: Dict):
        """Save benchmark results to file."""
        results_dir = PROJECT_ROOT / "tests" / "benchmark_results"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"{benchmark_name}_{timestamp}.json"
        
        # Convert dataclasses to dictionaries
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, BenchmarkMetrics):
                serializable_results[str(key)] = asdict(value)
            else:
                serializable_results[str(key)] = value
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"\nBenchmark results saved to: {results_file}")


class ResourceMonitor:
    """Monitors system resources during benchmarking."""
    
    def __init__(self, sample_interval: float = 0.5):
        self.sample_interval = sample_interval
        self.samples = []
        self.running = False
        self.thread = None
        
        self.peak_memory_mb = 0
        self.avg_memory_mb = 0
        self.peak_cpu_percent = 0
        self.avg_cpu_percent = 0
    
    def start(self):
        """Start resource monitoring."""
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()
    
    def stop(self):
        """Stop resource monitoring and calculate averages."""
        self.running = False
        if self.thread:
            self.thread.join()
        
        if self.samples:
            memory_values = [s["memory_mb"] for s in self.samples]
            cpu_values = [s["cpu_percent"] for s in self.samples]
            
            self.peak_memory_mb = max(memory_values)
            self.avg_memory_mb = statistics.mean(memory_values)
            self.peak_cpu_percent = max(cpu_values)
            self.avg_cpu_percent = statistics.mean(cpu_values)
    
    def _monitor(self):
        """Monitor system resources."""
        process = psutil.Process()
        
        while self.running:
            try:
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
                
                self.samples.append({
                    "timestamp": time.time(),
                    "memory_mb": memory_mb,
                    "cpu_percent": cpu_percent
                })
                
                time.sleep(self.sample_interval)
                
            except Exception:
                # Handle process monitoring errors gracefully
                break


if __name__ == "__main__":
    # Run performance benchmarks
    pytest.main([__file__, "-v", "-m", "benchmark"])