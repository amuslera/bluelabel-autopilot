#!/usr/bin/env python3
"""
Performance Analyzer

Analyzes system performance, detects bottlenecks, and provides optimization recommendations
for the BlueLabelAutopilot orchestration system.
"""

import json
import os
import psutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import argparse


@dataclass
class ResourceSnapshot:
    """System resource usage at a point in time"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    open_files: int
    threads: int
    

@dataclass 
class PerformanceBottleneck:
    """Identified performance bottleneck"""
    type: str  # cpu, memory, disk_io, file_handles, task_queue
    severity: str  # low, medium, high, critical
    description: str
    impact: str
    recommendation: str
    metrics: Dict[str, Any]
    

@dataclass
class TaskDistributionAnalysis:
    """Analysis of task distribution across agents"""
    agent_id: str
    workload_score: float  # 0-100, higher = more loaded
    pending_tasks: int
    estimated_hours: float
    avg_completion_time: float
    efficiency_score: float
    recommendations: List[str]


class PerformanceAnalyzer:
    """Analyzes system and orchestration performance"""
    
    def __init__(self, base_path: str = "/Users/arielmuslera/Development/Projects/bluelabel-autopilot"):
        self.base_path = Path(base_path)
        self.metrics_dir = self.base_path / ".metrics"
        self.cache_dir = self.base_path / ".cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Performance thresholds
        self.thresholds = {
            "cpu_percent_high": 80,
            "cpu_percent_critical": 95,
            "memory_percent_high": 75,
            "memory_percent_critical": 90,
            "disk_io_mb_high": 50,
            "open_files_high": 100,
            "task_queue_high": 10,
            "task_completion_slow": 2.0  # hours
        }
        
        # Resource monitoring
        self.resource_history = deque(maxlen=60)  # Keep last 60 snapshots
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 5):
        """Start background resource monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_resources,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop background resource monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_resources(self, interval: int):
        """Background thread for resource monitoring"""
        while self.monitoring_active:
            snapshot = self.capture_resource_snapshot()
            self.resource_history.append(snapshot)
            time.sleep(interval)
            
    def capture_resource_snapshot(self) -> ResourceSnapshot:
        """Capture current system resource usage"""
        # Get process info
        process = psutil.Process()
        
        # CPU usage (averaged over 0.1 seconds)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_io_read_mb = disk_io.read_bytes / 1024 / 1024 if disk_io else 0
        disk_io_write_mb = disk_io.write_bytes / 1024 / 1024 if disk_io else 0
        
        # File handles and threads
        try:
            open_files = len(process.open_files())
        except:
            open_files = 0
            
        threads = threading.active_count()
        
        return ResourceSnapshot(
            timestamp=datetime.now().isoformat() + 'Z',
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            open_files=open_files,
            threads=threads
        )
        
    def detect_bottlenecks(self) -> List[PerformanceBottleneck]:
        """Detect performance bottlenecks in the system"""
        bottlenecks = []
        
        # Analyze resource usage
        if self.resource_history:
            recent_snapshots = list(self.resource_history)[-10:]  # Last 10 snapshots
            
            # CPU bottleneck
            avg_cpu = statistics.mean(s.cpu_percent for s in recent_snapshots)
            max_cpu = max(s.cpu_percent for s in recent_snapshots)
            
            if avg_cpu > self.thresholds["cpu_percent_critical"]:
                bottlenecks.append(PerformanceBottleneck(
                    type="cpu",
                    severity="critical",
                    description=f"CPU usage critically high: {avg_cpu:.1f}% average",
                    impact="System may become unresponsive, tasks will execute slowly",
                    recommendation="Reduce concurrent task execution or optimize CPU-intensive operations",
                    metrics={"avg_cpu": avg_cpu, "max_cpu": max_cpu}
                ))
            elif avg_cpu > self.thresholds["cpu_percent_high"]:
                bottlenecks.append(PerformanceBottleneck(
                    type="cpu",
                    severity="high",
                    description=f"CPU usage high: {avg_cpu:.1f}% average",
                    impact="Task execution may be slower than optimal",
                    recommendation="Consider staggering task execution or adding CPU resources",
                    metrics={"avg_cpu": avg_cpu, "max_cpu": max_cpu}
                ))
                
            # Memory bottleneck
            avg_memory = statistics.mean(s.memory_percent for s in recent_snapshots)
            max_memory = max(s.memory_percent for s in recent_snapshots)
            
            if avg_memory > self.thresholds["memory_percent_critical"]:
                bottlenecks.append(PerformanceBottleneck(
                    type="memory",
                    severity="critical",
                    description=f"Memory usage critically high: {avg_memory:.1f}% average",
                    impact="System may crash or start swapping, severe performance degradation",
                    recommendation="Free up memory by clearing caches or reducing concurrent operations",
                    metrics={"avg_memory": avg_memory, "max_memory": max_memory}
                ))
                
            # File handle bottleneck
            avg_files = statistics.mean(s.open_files for s in recent_snapshots)
            if avg_files > self.thresholds["open_files_high"]:
                bottlenecks.append(PerformanceBottleneck(
                    type="file_handles",
                    severity="medium",
                    description=f"High number of open files: {avg_files:.0f} average",
                    impact="May hit system limits, causing file operation failures",
                    recommendation="Ensure files are properly closed after use",
                    metrics={"avg_open_files": avg_files}
                ))
                
        # Analyze task queue bottlenecks
        task_bottlenecks = self._analyze_task_queues()
        bottlenecks.extend(task_bottlenecks)
        
        # Analyze agent performance bottlenecks
        agent_bottlenecks = self._analyze_agent_performance()
        bottlenecks.extend(agent_bottlenecks)
        
        return bottlenecks
        
    def _analyze_task_queues(self) -> List[PerformanceBottleneck]:
        """Analyze task queue bottlenecks"""
        bottlenecks = []
        
        # Check each agent's task queue
        total_pending = 0
        overloaded_agents = []
        
        for agent_dir in (self.base_path / "postbox").iterdir():
            if agent_dir.is_dir():
                outbox_file = agent_dir / "outbox.json"
                if outbox_file.exists():
                    with open(outbox_file, 'r') as f:
                        data = json.load(f)
                        
                    pending_tasks = [t for t in data.get('tasks', []) if t.get('status') == 'pending']
                    total_pending += len(pending_tasks)
                    
                    if len(pending_tasks) > self.thresholds["task_queue_high"]:
                        overloaded_agents.append({
                            "agent": agent_dir.name,
                            "pending": len(pending_tasks),
                            "hours": sum(t.get('estimated_hours', 0) for t in pending_tasks)
                        })
                        
        if overloaded_agents:
            bottlenecks.append(PerformanceBottleneck(
                type="task_queue",
                severity="high" if len(overloaded_agents) > 2 else "medium",
                description=f"{len(overloaded_agents)} agents have overloaded task queues",
                impact="Tasks may be delayed, agents overwhelmed",
                recommendation="Redistribute tasks or increase agent capacity",
                metrics={"overloaded_agents": overloaded_agents, "total_pending": total_pending}
            ))
            
        return bottlenecks
        
    def _analyze_agent_performance(self) -> List[PerformanceBottleneck]:
        """Analyze individual agent performance"""
        bottlenecks = []
        
        # Load agent metrics
        slow_agents = []
        
        for metrics_file in (self.metrics_dir / "agents").glob("*_metrics.json"):
            with open(metrics_file, 'r') as f:
                agent_data = json.load(f)
                
            agent_id = agent_data['agent_id']
            summary = agent_data['summary']
            
            # Check for slow task completion
            if summary['avg_execution_time_hours'] > self.thresholds["task_completion_slow"]:
                slow_agents.append({
                    "agent": agent_id,
                    "avg_time": summary['avg_execution_time_hours'],
                    "efficiency": summary['avg_efficiency_score']
                })
                
        if slow_agents:
            bottlenecks.append(PerformanceBottleneck(
                type="agent_performance",
                severity="medium",
                description=f"{len(slow_agents)} agents have slow task completion times",
                impact="Overall system throughput reduced",
                recommendation="Review task complexity and agent capabilities",
                metrics={"slow_agents": slow_agents}
            ))
            
        return bottlenecks
        
    def analyze_task_distribution(self) -> List[TaskDistributionAnalysis]:
        """Analyze how tasks are distributed across agents"""
        analyses = []
        
        for agent_dir in (self.base_path / "postbox").iterdir():
            if not agent_dir.is_dir():
                continue
                
            agent_id = agent_dir.name
            outbox_file = agent_dir / "outbox.json"
            
            if not outbox_file.exists():
                continue
                
            with open(outbox_file, 'r') as f:
                data = json.load(f)
                
            # Calculate workload
            pending_tasks = [t for t in data.get('tasks', []) if t.get('status') == 'pending']
            pending_count = len(pending_tasks)
            estimated_hours = sum(t.get('estimated_hours', 0) for t in pending_tasks)
            
            # Get performance metrics
            metrics_file = self.metrics_dir / f"agents/{agent_id}_metrics.json"
            avg_completion_time = 0
            efficiency_score = 0
            
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                    avg_completion_time = metrics_data['summary']['avg_execution_time_hours']
                    efficiency_score = metrics_data['summary']['avg_efficiency_score']
                    
            # Calculate workload score (0-100)
            workload_score = min(100, (estimated_hours / 8) * 100)  # 8 hours = 100%
            
            # Generate recommendations
            recommendations = []
            if workload_score > 80:
                recommendations.append("Agent is overloaded, consider redistributing tasks")
            elif workload_score < 20:
                recommendations.append("Agent has capacity for additional tasks")
                
            if efficiency_score < 70:
                recommendations.append("Review task assignments for better agent-task matching")
                
            analyses.append(TaskDistributionAnalysis(
                agent_id=agent_id,
                workload_score=workload_score,
                pending_tasks=pending_count,
                estimated_hours=estimated_hours,
                avg_completion_time=avg_completion_time,
                efficiency_score=efficiency_score,
                recommendations=recommendations
            ))
            
        return sorted(analyses, key=lambda x: x.workload_score, reverse=True)
        
    def optimize_task_distribution(self, analyses: List[TaskDistributionAnalysis]) -> Dict[str, List[str]]:
        """Generate task redistribution recommendations"""
        recommendations = defaultdict(list)
        
        # Find overloaded and underutilized agents
        overloaded = [a for a in analyses if a.workload_score > 80]
        underutilized = [a for a in analyses if a.workload_score < 30]
        
        if overloaded and underutilized:
            for over_agent in overloaded:
                for under_agent in underutilized:
                    # Check expertise compatibility
                    if self._check_expertise_compatibility(over_agent.agent_id, under_agent.agent_id):
                        recommendations[over_agent.agent_id].append(
                            f"Consider moving tasks to {under_agent.agent_id} (currently at {under_agent.workload_score:.0f}% capacity)"
                        )
                        
        # Recommend based on efficiency scores
        high_efficiency = [a for a in analyses if a.efficiency_score > 85]
        for agent in high_efficiency:
            if agent.workload_score < 60:
                recommendations["general"].append(
                    f"{agent.agent_id} has high efficiency ({agent.efficiency_score:.0f}%) and available capacity"
                )
                
        return dict(recommendations)
        
    def _check_expertise_compatibility(self, agent1: str, agent2: str) -> bool:
        """Check if two agents have compatible expertise"""
        # Load expertise from outbox files
        expertise_map = {}
        
        for agent_id in [agent1, agent2]:
            outbox_file = self.base_path / f"postbox/{agent_id}/outbox.json"
            if outbox_file.exists():
                with open(outbox_file, 'r') as f:
                    data = json.load(f)
                    expertise_map[agent_id] = set(data.get('expertise', []))
                    
        # Check for overlap
        if agent1 in expertise_map and agent2 in expertise_map:
            overlap = expertise_map[agent1] & expertise_map[agent2]
            return len(overlap) > 0
            
        return False
        
    def create_performance_cache(self, key: str, data: Any, ttl_seconds: int = 300):
        """Create cached data for performance optimization"""
        cache_file = self.cache_dir / f"{key}.json"
        cache_data = {
            "data": data,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
            
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Retrieve cached data if not expired"""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
            
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
            
        # Check expiration
        expires_at = datetime.fromisoformat(cache_data['expires_at'])
        if datetime.now() > expires_at:
            cache_file.unlink()  # Delete expired cache
            return None
            
        return cache_data['data']
        
    def run_benchmark(self, operations: List[str] = None) -> Dict[str, float]:
        """Run performance benchmarks"""
        if operations is None:
            operations = ["file_read", "json_parse", "metric_calculation", "cache_operation"]
            
        results = {}
        
        # Benchmark file operations
        if "file_read" in operations:
            start = time.time()
            for _ in range(100):
                test_file = self.base_path / "postbox/CB/outbox.json"
                if test_file.exists():
                    with open(test_file, 'r') as f:
                        _ = f.read()
            results["file_read_100x"] = time.time() - start
            
        # Benchmark JSON parsing
        if "json_parse" in operations:
            test_data = '{"test": [1, 2, 3], "nested": {"data": "value"}}'
            start = time.time()
            for _ in range(1000):
                _ = json.loads(test_data)
            results["json_parse_1000x"] = time.time() - start
            
        # Benchmark metric calculations
        if "metric_calculation" in operations:
            test_numbers = list(range(1000))
            start = time.time()
            for _ in range(100):
                _ = statistics.mean(test_numbers)
                _ = statistics.stdev(test_numbers)
                _ = min(test_numbers)
                _ = max(test_numbers)
            results["metric_calc_100x"] = time.time() - start
            
        # Benchmark cache operations
        if "cache_operation" in operations:
            start = time.time()
            for i in range(50):
                self.create_performance_cache(f"benchmark_test_{i}", {"data": i})
                _ = self.get_cached_data(f"benchmark_test_{i}")
            results["cache_ops_50x"] = time.time() - start
            
            # Cleanup
            for i in range(50):
                cache_file = self.cache_dir / f"benchmark_test_{i}.json"
                if cache_file.exists():
                    cache_file.unlink()
                    
        return results
        
    def generate_recommendations(self, bottlenecks: List[PerformanceBottleneck], 
                               distribution: List[TaskDistributionAnalysis]) -> Dict[str, Any]:
        """Generate comprehensive performance recommendations"""
        recommendations = {
            "timestamp": datetime.now().isoformat() + 'Z',
            "critical_issues": [],
            "optimizations": [],
            "tuning_parameters": {},
            "action_items": []
        }
        
        # Process bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck.severity == "critical":
                recommendations["critical_issues"].append({
                    "type": bottleneck.type,
                    "description": bottleneck.description,
                    "action": bottleneck.recommendation
                })
                
        # Task distribution optimizations
        overloaded_agents = [a for a in distribution if a.workload_score > 80]
        if overloaded_agents:
            recommendations["optimizations"].append({
                "category": "task_distribution",
                "issue": f"{len(overloaded_agents)} agents are overloaded",
                "suggestion": "Implement dynamic task redistribution based on agent capacity"
            })
            
        # Performance tuning parameters
        if any(b.type == "cpu" for b in bottlenecks):
            recommendations["tuning_parameters"]["max_concurrent_tasks"] = 3
        else:
            recommendations["tuning_parameters"]["max_concurrent_tasks"] = 5
            
        if any(b.type == "memory" for b in bottlenecks):
            recommendations["tuning_parameters"]["cache_ttl_seconds"] = 60
        else:
            recommendations["tuning_parameters"]["cache_ttl_seconds"] = 300
            
        # Action items
        recommendations["action_items"] = [
            "Review and implement critical issue resolutions",
            "Apply recommended tuning parameters",
            "Schedule regular performance reviews",
            "Consider implementing auto-scaling for peak loads"
        ]
        
        return recommendations


def main():
    """CLI interface for performance analyzer"""
    parser = argparse.ArgumentParser(description="Performance Analysis Tool")
    parser.add_argument("command", choices=["analyze", "monitor", "benchmark", "optimize"],
                       help="Command to execute")
    parser.add_argument("--duration", type=int, default=60, 
                       help="Monitoring duration in seconds (for monitor command)")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer()
    
    if args.command == "analyze":
        # Start brief monitoring to collect data
        print("Collecting resource data...")
        analyzer.start_monitoring(interval=1)
        time.sleep(10)
        analyzer.stop_monitoring()
        
        # Detect bottlenecks
        bottlenecks = analyzer.detect_bottlenecks()
        distribution = analyzer.analyze_task_distribution()
        recommendations = analyzer.generate_recommendations(bottlenecks, distribution)
        
        # Display results
        print("\n🔍 PERFORMANCE ANALYSIS REPORT")
        print("=" * 60)
        
        if bottlenecks:
            print("\n⚠️  BOTTLENECKS DETECTED:")
            for b in bottlenecks:
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                print(f"\n{severity_emoji.get(b.severity, '⚪')} {b.type.upper()} ({b.severity})")
                print(f"   {b.description}")
                print(f"   Impact: {b.impact}")
                print(f"   Fix: {b.recommendation}")
        else:
            print("\n✅ No bottlenecks detected")
            
        print("\n📊 TASK DISTRIBUTION:")
        for agent in distribution:
            print(f"\n{agent.agent_id}:")
            print(f"   Workload: {agent.workload_score:.0f}%")
            print(f"   Pending: {agent.pending_tasks} tasks ({agent.estimated_hours:.1f} hours)")
            print(f"   Efficiency: {agent.efficiency_score:.0f}%")
            
        # Save results if requested
        if args.output:
            output_data = {
                "bottlenecks": [asdict(b) for b in bottlenecks],
                "distribution": [asdict(d) for d in distribution],
                "recommendations": recommendations
            }
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
            
    elif args.command == "monitor":
        print(f"Starting resource monitoring for {args.duration} seconds...")
        analyzer.start_monitoring(interval=2)
        
        try:
            for i in range(args.duration):
                if analyzer.resource_history:
                    latest = analyzer.resource_history[-1]
                    print(f"\rCPU: {latest.cpu_percent:5.1f}% | "
                          f"Memory: {latest.memory_percent:5.1f}% | "
                          f"Files: {latest.open_files:3d} | "
                          f"Threads: {latest.threads:3d}", end='', flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            analyzer.stop_monitoring()
            print("\n\nMonitoring stopped")
            
    elif args.command == "benchmark":
        print("Running performance benchmarks...")
        results = analyzer.run_benchmark()
        
        print("\n⚡ BENCHMARK RESULTS:")
        print("=" * 40)
        for operation, duration in results.items():
            print(f"{operation:20s}: {duration:8.4f}s")
            
    elif args.command == "optimize":
        distribution = analyzer.analyze_task_distribution()
        optimize_recommendations = analyzer.optimize_task_distribution(distribution)
        
        print("\n🎯 OPTIMIZATION RECOMMENDATIONS:")
        print("=" * 60)
        
        for agent, recs in optimize_recommendations.items():
            print(f"\n{agent}:")
            for rec in recs:
                print(f"  - {rec}")


if __name__ == "__main__":
    main()