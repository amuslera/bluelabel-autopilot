#!/usr/bin/env python3
"""
Performance Profiling Suite for Bluelabel Autopilot
Measures execution times, memory usage, and system performance metrics.
"""

import asyncio
import time
import tracemalloc
import psutil
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import concurrent.futures
from dataclasses import dataclass, asdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.unified_workflow_adapter import UnifiedWorkflowAdapter
from core.agent_registry import register_agent
from agents.ingestion_agent import IngestionAgent
from agents.digest_agent import DigestAgent


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    operation: str
    start_time: float
    end_time: float
    duration_ms: float
    memory_start_mb: float
    memory_peak_mb: float
    memory_delta_mb: float
    cpu_percent: float
    success: bool
    error: str = None
    metadata: Dict[str, Any] = None


class PerformanceProfiler:
    """Comprehensive performance profiling for workflow execution."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process(os.getpid())
        
    def measure_operation(self, operation_name: str):
        """Context manager for measuring operation performance."""
        class OperationMeasurer:
            def __init__(self, profiler, name):
                self.profiler = profiler
                self.name = name
                self.start_time = None
                self.start_memory = None
                self.cpu_start = None
                
            def __enter__(self):
                # Start measurements
                self.start_time = time.time()
                self.start_memory = self.profiler.process.memory_info().rss / 1024 / 1024  # MB
                self.cpu_start = self.profiler.process.cpu_percent(interval=0.1)
                tracemalloc.start()
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                # End measurements
                end_time = time.time()
                duration_ms = (end_time - self.start_time) * 1000
                
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                end_memory = self.profiler.process.memory_info().rss / 1024 / 1024
                peak_memory = max(end_memory, self.start_memory + (peak / 1024 / 1024))
                
                cpu_percent = self.profiler.process.cpu_percent(interval=0.1)
                
                # Record metrics
                metric = PerformanceMetrics(
                    operation=self.name,
                    start_time=self.start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    memory_start_mb=self.start_memory,
                    memory_peak_mb=peak_memory,
                    memory_delta_mb=end_memory - self.start_memory,
                    cpu_percent=cpu_percent,
                    success=exc_type is None,
                    error=str(exc_val) if exc_val else None
                )
                
                self.profiler.metrics.append(metric)
                
        return OperationMeasurer(self, operation_name)
    
    async def profile_workflow_execution(self, workflow_yaml: str, inputs: Dict[str, Any]) -> str:
        """Profile a single workflow execution."""
        with self.measure_operation("workflow_total"):
            # Initialize adapter
            with self.measure_operation("adapter_init"):
                adapter = UnifiedWorkflowAdapter()
            
            # Run workflow
            with self.measure_operation("workflow_execution"):
                run_id = await adapter.run_workflow(
                    workflow_name="perf-test",
                    inputs=inputs,
                    workflow_yaml=workflow_yaml
                )
            
            # Monitor until complete
            with self.measure_operation("workflow_monitoring"):
                while True:
                    status = adapter.get_run_status(run_id)
                    if status and status["status"] in ["success", "failed", "cancelled"]:
                        break
                    await asyncio.sleep(0.1)
            
            return run_id
    
    async def profile_concurrent_workflows(self, count: int) -> List[str]:
        """Profile multiple concurrent workflow executions."""
        workflow_yaml = """
name: concurrent-test
version: 1.0.0
description: Concurrent execution test

steps:
  - name: ingest
    agent: ingestion
    input:
      text: "Test document for concurrent execution {{workflow_id}}"
    output: content

  - name: digest
    agent: digest
    input:
      content: "{{content}}"
    output: summary
"""
        
        with self.measure_operation(f"concurrent_workflows_{count}"):
            tasks = []
            for i in range(count):
                inputs = {"workflow_id": i}
                task = self.profile_workflow_execution(workflow_yaml, inputs)
                tasks.append(task)
            
            run_ids = await asyncio.gather(*tasks)
            return run_ids
    
    async def profile_large_pdf_processing(self, pdf_path: Path) -> str:
        """Profile large PDF processing performance."""
        workflow_yaml = """
name: pdf-processing-test
version: 1.0.0
description: Large PDF processing test

steps:
  - name: ingest_pdf
    agent: ingestion
    input:
      type: pdf
      file_path: "{{pdf_path}}"
    output: pdf_content

  - name: create_digest
    agent: digest
    input:
      content: "{{pdf_content}}"
    output: pdf_summary
"""
        
        file_size_mb = pdf_path.stat().st_size / 1024 / 1024
        
        with self.measure_operation(f"large_pdf_{file_size_mb:.1f}MB"):
            return await self.profile_workflow_execution(
                workflow_yaml,
                {"pdf_path": str(pdf_path)}
            )
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Generate summary statistics from collected metrics."""
        if not self.metrics:
            return {}
        
        # Group by operation type
        operation_stats = {}
        for metric in self.metrics:
            op = metric.operation
            if op not in operation_stats:
                operation_stats[op] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                    "min_duration_ms": float('inf'),
                    "max_duration_ms": 0,
                    "avg_memory_delta_mb": 0,
                    "max_memory_peak_mb": 0,
                    "success_rate": 0,
                    "errors": []
                }
            
            stats = operation_stats[op]
            stats["count"] += 1
            stats["total_duration_ms"] += metric.duration_ms
            stats["min_duration_ms"] = min(stats["min_duration_ms"], metric.duration_ms)
            stats["max_duration_ms"] = max(stats["max_duration_ms"], metric.duration_ms)
            stats["max_memory_peak_mb"] = max(stats["max_memory_peak_mb"], metric.memory_peak_mb)
            
            if metric.error:
                stats["errors"].append(metric.error)
        
        # Calculate averages
        for op, stats in operation_stats.items():
            count = stats["count"]
            stats["avg_duration_ms"] = stats["total_duration_ms"] / count
            
            # Calculate memory average
            memory_deltas = [m.memory_delta_mb for m in self.metrics if m.operation == op]
            stats["avg_memory_delta_mb"] = sum(memory_deltas) / len(memory_deltas)
            
            # Calculate success rate
            successes = sum(1 for m in self.metrics if m.operation == op and m.success)
            stats["success_rate"] = (successes / count) * 100
        
        return {
            "total_operations": len(self.metrics),
            "operation_statistics": operation_stats,
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "available_memory_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024
            }
        }
    
    def save_results(self, filepath: Path):
        """Save profiling results to JSON file."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": [asdict(m) for m in self.metrics],
            "summary": self.get_summary_statistics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)


async def run_performance_profile():
    """Run comprehensive performance profiling suite."""
    print("🔍 Starting Performance Profiling Suite...")
    
    # Register agents
    register_agent('ingestion', IngestionAgent)
    register_agent('digest', DigestAgent)
    
    profiler = PerformanceProfiler()
    
    # 1. Profile single workflow execution
    print("\n1️⃣ Profiling single workflow execution...")
    simple_workflow = """
name: simple-test
version: 1.0.0
steps:
  - name: step1
    agent: ingestion
    input:
      text: "Simple test document"
    output: result
"""
    await profiler.profile_workflow_execution(simple_workflow, {})
    
    # 2. Profile concurrent workflows
    print("\n2️⃣ Profiling concurrent workflow execution...")
    for count in [5, 10, 20]:
        print(f"   Testing {count} concurrent workflows...")
        await profiler.profile_concurrent_workflows(count)
    
    # 3. Profile large PDF processing (if test files exist)
    print("\n3️⃣ Profiling large PDF processing...")
    test_pdfs = [
        Path("tests/stress_test_5mb.pdf"),
        Path("tests/stress_test_100pages.pdf"),
        Path("tests/stress_test_200pages.pdf")
    ]
    
    for pdf_path in test_pdfs:
        if pdf_path.exists():
            print(f"   Processing {pdf_path.name}...")
            await profiler.profile_large_pdf_processing(pdf_path)
        else:
            print(f"   ⚠️  Skipping {pdf_path.name} (not found)")
    
    # 4. Generate and save results
    print("\n4️⃣ Generating performance report...")
    summary = profiler.get_summary_statistics()
    
    # Print summary
    print("\n📊 Performance Summary:")
    print(f"Total operations profiled: {summary['total_operations']}")
    
    for op, stats in summary['operation_statistics'].items():
        print(f"\n{op}:")
        print(f"  - Count: {stats['count']}")
        print(f"  - Avg Duration: {stats['avg_duration_ms']:.2f}ms")
        print(f"  - Min/Max Duration: {stats['min_duration_ms']:.2f}ms / {stats['max_duration_ms']:.2f}ms")
        print(f"  - Avg Memory Delta: {stats['avg_memory_delta_mb']:.2f}MB")
        print(f"  - Success Rate: {stats['success_rate']:.1f}%")
    
    # Save results
    results_path = Path("docs/PERFORMANCE_BASELINE.json")
    results_path.parent.mkdir(exist_ok=True)
    profiler.save_results(results_path)
    print(f"\n✅ Results saved to {results_path}")
    
    return profiler


if __name__ == "__main__":
    asyncio.run(run_performance_profile())