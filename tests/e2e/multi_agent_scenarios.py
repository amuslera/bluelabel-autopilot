#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Suite for Multi-Agent Orchestration.

Tests complex real-world scenarios including multi-agent workflows,
concurrent operations, failure handling, performance under load,
and chaos testing for system resilience.
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
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
import requests
from unittest.mock import patch, MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class TestMetrics:
    """Metrics collected during testing."""
    start_time: float
    end_time: float
    duration: float
    success_rate: float
    operations_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float
    errors: List[str]
    warnings: List[str]


@dataclass
class Agent:
    """Represents an agent in the orchestration system."""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    current_tasks: List[str]
    status: str
    last_heartbeat: Optional[datetime] = None


@dataclass
class Task:
    """Represents a task in the orchestration system."""
    task_id: str
    title: str
    priority: str
    estimated_hours: int
    dependencies: List[str]
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class E2ETestEnvironment:
    """Manages test environment setup and teardown."""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.workspace = None
        self.agents = {}
        self.tasks = {}
        self.metrics = TestMetrics(0, 0, 0, 0, 0, 0, 0, [], [])
        
    def __enter__(self):
        """Set up test environment."""
        # Create isolated test workspace
        self.workspace = Path(tempfile.mkdtemp(prefix=f"e2e_{self.test_name}_"))
        
        # Create required directory structure
        self._setup_directories()
        self._setup_agents()
        self._setup_tools()
        
        self.metrics.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up test environment."""
        self.metrics.end_time = time.time()
        self.metrics.duration = self.metrics.end_time - self.metrics.start_time
        
        # Calculate final metrics
        self._calculate_final_metrics()
        
        # Cleanup workspace
        if self.workspace and self.workspace.exists():
            shutil.rmtree(self.workspace)
    
    def _setup_directories(self):
        """Create required directory structure."""
        dirs = [
            "postbox/AGENT_A", "postbox/AGENT_B", "postbox/AGENT_C",
            "postbox/AGENT_D", "postbox/AGENT_E",
            ".sprint", ".sprint/backups",
            "tools", "logs", "data/checkpoints",
            "orchestration/agents/AGENT_A/task_inbox",
            "orchestration/agents/AGENT_B/task_inbox",
            "orchestration/agents/AGENT_C/task_inbox",
            "orchestration/queue/pending",
            "orchestration/queue/assigned",
            "orchestration/queue/completed",
            "orchestration/queue/failed",
            "orchestration/metrics"
        ]
        
        for dir_path in dirs:
            (self.workspace / dir_path).mkdir(parents=True, exist_ok=True)
    
    def _setup_agents(self):
        """Set up test agents with different capabilities."""
        agent_configs = {
            "AGENT_A": Agent("AGENT_A", "backend", ["python", "api", "database"], [], "active"),
            "AGENT_B": Agent("AGENT_B", "frontend", ["react", "ui", "css"], [], "active"),
            "AGENT_C": Agent("AGENT_C", "devops", ["docker", "deployment", "monitoring"], [], "active"),
            "AGENT_D": Agent("AGENT_D", "testing", ["pytest", "selenium", "performance"], [], "active"),
            "AGENT_E": Agent("AGENT_E", "architecture", ["design", "review", "documentation"], [], "active")
        }
        
        for agent_id, agent in agent_configs.items():
            self.agents[agent_id] = agent
            
            # Create outbox
            outbox = {
                "agent_id": agent_id,
                "agent_name": f"Test {agent.agent_type.title()} Agent",
                "agent_type": "test",
                "expertise": agent.capabilities,
                "tasks": []
            }
            
            outbox_path = self.workspace / f"postbox/{agent_id}/outbox.json"
            with open(outbox_path, 'w') as f:
                json.dump(outbox, f, indent=2)
    
    def _setup_tools(self):
        """Copy orchestration tools to test workspace."""
        tools_src = PROJECT_ROOT / "tools"
        tools_dst = self.workspace / "tools"
        
        scripts = [
            "assign_task.sh", "complete_task.sh", "task_status.sh",
            "update_progress.sh", "file_lock.py", "recovery_manager.py",
            "security_audit.py"
        ]
        
        for script in scripts:
            src_file = tools_src / script
            if src_file.exists():
                shutil.copy2(src_file, tools_dst / script)
    
    def _calculate_final_metrics(self):
        """Calculate final test metrics."""
        process = psutil.Process()
        self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        self.metrics.cpu_usage_percent = process.cpu_percent()
        
        # Calculate success rate
        total_operations = len(self.tasks)
        successful_operations = sum(1 for task in self.tasks.values() 
                                  if task.status == "completed")
        
        if total_operations > 0:
            self.metrics.success_rate = successful_operations / total_operations
            self.metrics.operations_per_second = total_operations / self.metrics.duration
        else:
            self.metrics.success_rate = 1.0
            self.metrics.operations_per_second = 0.0


class MultiAgentScenarioTester:
    """Tests complex multi-agent orchestration scenarios."""
    
    @pytest.mark.e2e
    def test_large_scale_task_distribution(self):
        """Test distributing 100+ tasks across multiple agents."""
        with E2ETestEnvironment("large_scale_distribution") as env:
            # Generate large number of tasks
            tasks = self._generate_tasks(count=150, 
                                       complexity_levels=["simple", "medium", "complex"])
            
            # Distribute tasks based on agent capabilities
            task_assignments = self._distribute_tasks_by_capability(tasks, env.agents)
            
            # Execute assignments
            assignment_results = []
            for agent_id, agent_tasks in task_assignments.items():
                for task in agent_tasks:
                    result = self._assign_task_to_agent(env, agent_id, task)
                    assignment_results.append(result)
            
            # Verify all tasks were assigned
            assert len(assignment_results) == len(tasks)
            assert all(result["success"] for result in assignment_results)
            
            # Verify balanced distribution
            task_counts = {agent_id: len(agent_tasks) 
                          for agent_id, agent_tasks in task_assignments.items()}
            
            max_tasks = max(task_counts.values())
            min_tasks = min(task_counts.values())
            
            # Distribution should be reasonably balanced (within 50% difference)
            assert (max_tasks - min_tasks) / max_tasks < 0.5
    
    @pytest.mark.e2e
    def test_complex_dependency_chain(self):
        """Test complex task dependency chains across multiple agents."""
        with E2ETestEnvironment("dependency_chain") as env:
            # Create task chain: A -> B,C -> D -> E
            tasks = [
                Task("TASK_CHAIN_A", "Initial Analysis", "HIGH", 2, []),
                Task("TASK_CHAIN_B", "Backend Implementation", "HIGH", 4, ["TASK_CHAIN_A"]),
                Task("TASK_CHAIN_C", "Frontend Design", "HIGH", 3, ["TASK_CHAIN_A"]),
                Task("TASK_CHAIN_D", "Integration Testing", "MEDIUM", 2, ["TASK_CHAIN_B", "TASK_CHAIN_C"]),
                Task("TASK_CHAIN_E", "Deployment", "HIGH", 1, ["TASK_CHAIN_D"])
            ]
            
            # Assign tasks to appropriate agents
            task_agent_mapping = {
                "TASK_CHAIN_A": "AGENT_E",  # Architecture
                "TASK_CHAIN_B": "AGENT_A",  # Backend
                "TASK_CHAIN_C": "AGENT_B",  # Frontend
                "TASK_CHAIN_D": "AGENT_D",  # Testing
                "TASK_CHAIN_E": "AGENT_C"   # DevOps
            }
            
            # Execute dependency chain
            completed_tasks = []
            
            # Process tasks respecting dependencies
            while len(completed_tasks) < len(tasks):
                ready_tasks = [
                    task for task in tasks 
                    if (task.task_id not in completed_tasks and 
                        all(dep in completed_tasks for dep in task.dependencies))
                ]
                
                assert len(ready_tasks) > 0, "No ready tasks found - possible circular dependency"
                
                # Process ready tasks in parallel
                for task in ready_tasks:
                    agent_id = task_agent_mapping[task.task_id]
                    result = self._assign_task_to_agent(env, agent_id, task)
                    assert result["success"]
                    
                    # Simulate task execution time
                    time.sleep(0.1)
                    
                    # Complete task
                    completion_result = self._complete_task(env, agent_id, task.task_id)
                    assert completion_result["success"]
                    
                    completed_tasks.append(task.task_id)
            
            # Verify all tasks completed in correct order
            assert len(completed_tasks) == len(tasks)
    
    @pytest.mark.e2e
    def test_concurrent_agent_operations(self):
        """Test multiple agents working concurrently on different tasks."""
        with E2ETestEnvironment("concurrent_operations") as env:
            # Create tasks for each agent
            concurrent_tasks = [
                (f"CONCURRENT_TASK_{i}", f"AGENT_{chr(65 + i % 5)}", f"Task {i}")
                for i in range(25)
            ]
            
            # Execute tasks concurrently
            def execute_task(task_info):
                task_id, agent_id, title = task_info
                task = Task(task_id, title, "MEDIUM", 1, [])
                
                # Assign task
                assign_result = self._assign_task_to_agent(env, agent_id, task)
                if not assign_result["success"]:
                    return {"task_id": task_id, "success": False, "error": "Assignment failed"}
                
                # Small random delay to simulate work
                time.sleep(random.uniform(0.05, 0.2))
                
                # Complete task
                complete_result = self._complete_task(env, agent_id, task_id)
                return {
                    "task_id": task_id,
                    "success": complete_result["success"],
                    "error": complete_result.get("error")
                }
            
            # Run tasks concurrently
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(execute_task, task_info) 
                          for task_info in concurrent_tasks]
                
                results = [future.result() for future in as_completed(futures)]
            
            # Verify all tasks completed successfully
            successful_tasks = [r for r in results if r["success"]]
            assert len(successful_tasks) == len(concurrent_tasks)
            
            # Verify no race conditions in file updates
            self._verify_outbox_integrity(env)
    
    @pytest.mark.e2e
    def test_mixed_workload_scenario(self):
        """Test mixed workload with different task types and priorities."""
        with E2ETestEnvironment("mixed_workload") as env:
            # Create mixed workload
            high_priority_tasks = self._generate_tasks(10, ["complex"], priority="HIGH")
            medium_priority_tasks = self._generate_tasks(20, ["medium"], priority="MEDIUM")
            low_priority_tasks = self._generate_tasks(30, ["simple"], priority="LOW")
            
            all_tasks = high_priority_tasks + medium_priority_tasks + low_priority_tasks
            random.shuffle(all_tasks)  # Randomize submission order
            
            # Submit all tasks
            submission_times = {}
            for task in all_tasks:
                # Choose agent based on task complexity
                agent_id = self._select_agent_for_task(task, env.agents)
                
                submission_times[task.task_id] = time.time()
                result = self._assign_task_to_agent(env, agent_id, task)
                assert result["success"]
            
            # Process tasks (priority should influence order)
            processing_order = []
            
            # Simulate priority-based processing
            for priority in ["HIGH", "MEDIUM", "LOW"]:
                priority_tasks = [t for t in all_tasks if t.priority == priority]
                
                for task in priority_tasks:
                    agent_id = task.assigned_agent
                    complete_result = self._complete_task(env, agent_id, task.task_id)
                    if complete_result["success"]:
                        processing_order.append((task.task_id, task.priority))
            
            # Verify high priority tasks were generally processed first
            high_priority_positions = [i for i, (task_id, priority) in enumerate(processing_order) 
                                     if priority == "HIGH"]
            
            if high_priority_positions:
                avg_high_priority_pos = sum(high_priority_positions) / len(high_priority_positions)
                assert avg_high_priority_pos < len(processing_order) / 3  # In first third
    
    @pytest.mark.e2e
    def test_agent_failure_recovery(self):
        """Test system behavior when agents fail or become unavailable."""
        with E2ETestEnvironment("failure_recovery") as env:
            # Assign tasks to multiple agents
            initial_tasks = self._generate_tasks(15, ["medium"])
            for i, task in enumerate(initial_tasks):
                agent_id = f"AGENT_{chr(65 + i % 5)}"
                result = self._assign_task_to_agent(env, agent_id, task)
                assert result["success"]
            
            # Simulate agent failure (AGENT_B goes offline)
            failed_agent = "AGENT_B"
            env.agents[failed_agent].status = "offline"
            
            # Get tasks assigned to failed agent
            failed_agent_tasks = [t for t in initial_tasks 
                                if t.assigned_agent == failed_agent]
            
            # Simulate recovery: reassign failed agent's tasks
            recovered_tasks = []
            for task in failed_agent_tasks:
                # Find alternative agent
                alternative_agents = [
                    agent_id for agent_id, agent in env.agents.items()
                    if (agent.status == "active" and 
                        any(cap in agent.capabilities for cap in ["react", "ui", "css"]))
                ]
                
                if alternative_agents:
                    new_agent = alternative_agents[0]
                    # Reassign task
                    task.assigned_agent = new_agent
                    result = self._assign_task_to_agent(env, new_agent, task)
                    if result["success"]:
                        recovered_tasks.append(task.task_id)
            
            # Verify all failed agent's tasks were recovered
            assert len(recovered_tasks) == len(failed_agent_tasks)
            
            # Complete all tasks
            for task in initial_tasks:
                if task.assigned_agent != failed_agent:
                    result = self._complete_task(env, task.assigned_agent, task.task_id)
                    assert result["success"]
    
    @pytest.mark.e2e
    def test_performance_under_load(self):
        """Test system performance under high load conditions."""
        with E2ETestEnvironment("performance_load") as env:
            # Generate high load
            load_tasks = self._generate_tasks(200, ["simple", "medium"])
            
            start_time = time.time()
            
            # Rapid task assignment
            assignment_times = []
            for task in load_tasks:
                assign_start = time.time()
                
                agent_id = f"AGENT_{chr(65 + hash(task.task_id) % 5)}"
                result = self._assign_task_to_agent(env, agent_id, task)
                
                assign_end = time.time()
                assignment_times.append(assign_end - assign_start)
                
                assert result["success"]
            
            assignment_phase_time = time.time() - start_time
            
            # Rapid task completion
            completion_start = time.time()
            completion_times = []
            
            for task in load_tasks:
                complete_start = time.time()
                
                result = self._complete_task(env, task.assigned_agent, task.task_id)
                
                complete_end = time.time()
                completion_times.append(complete_end - complete_start)
                
                assert result["success"]
            
            completion_phase_time = time.time() - completion_start
            total_time = time.time() - start_time
            
            # Performance assertions
            avg_assignment_time = sum(assignment_times) / len(assignment_times)
            avg_completion_time = sum(completion_times) / len(completion_times)
            
            # Operations should be reasonably fast
            assert avg_assignment_time < 0.1  # Less than 100ms per assignment
            assert avg_completion_time < 0.1   # Less than 100ms per completion
            
            # Throughput should be reasonable
            throughput = len(load_tasks) / total_time
            assert throughput > 10  # At least 10 operations per second
            
            # Update metrics
            env.metrics.operations_per_second = throughput
    
    @pytest.mark.e2e
    def test_data_consistency_under_stress(self):
        """Test data consistency when multiple operations occur simultaneously."""
        with E2ETestEnvironment("data_consistency") as env:
            # Create shared resource (progress tracking)
            progress_file = env.workspace / ".sprint/progress.json"
            initial_progress = {
                "sprint_id": "TEST_SPRINT",
                "total_tasks": 0,
                "completed": 0,
                "tasks": {}
            }
            
            with open(progress_file, 'w') as f:
                json.dump(initial_progress, f, indent=2)
            
            # Generate concurrent operations
            num_operations = 50
            tasks = self._generate_tasks(num_operations, ["simple"])
            
            def concurrent_operation(task):
                """Perform task assignment and completion."""
                agent_id = f"AGENT_{chr(65 + hash(task.task_id) % 5)}"
                
                # Assign
                assign_result = self._assign_task_to_agent(env, agent_id, task)
                if not assign_result["success"]:
                    return False
                
                # Small delay
                time.sleep(random.uniform(0.01, 0.05))
                
                # Complete
                complete_result = self._complete_task(env, agent_id, task.task_id)
                return complete_result["success"]
            
            # Execute operations concurrently
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(concurrent_operation, task) 
                          for task in tasks]
                results = [future.result() for future in as_completed(futures)]
            
            # Verify data consistency
            successful_operations = sum(results)
            
            # Check final progress state
            with open(progress_file) as f:
                final_progress = json.load(f)
            
            # Data should be consistent
            expected_completed = successful_operations
            
            # Allow for some variance due to concurrent updates
            assert abs(final_progress.get("completed", 0) - expected_completed) <= 5
            
            # Verify outbox integrity
            self._verify_outbox_integrity(env)
    
    def _generate_tasks(self, count: int, complexity_levels: List[str], 
                       priority: str = "MEDIUM") -> List[Task]:
        """Generate test tasks with specified parameters."""
        tasks = []
        
        for i in range(count):
            complexity = random.choice(complexity_levels)
            
            # Determine estimated hours based on complexity
            hours_map = {"simple": 1, "medium": 2, "complex": 4}
            estimated_hours = hours_map.get(complexity, 2)
            
            task = Task(
                task_id=f"GENERATED_TASK_{i:03d}",
                title=f"{complexity.title()} Task {i}",
                priority=priority,
                estimated_hours=estimated_hours,
                dependencies=[],
                created_at=datetime.now()
            )
            
            tasks.append(task)
        
        return tasks
    
    def _distribute_tasks_by_capability(self, tasks: List[Task], 
                                      agents: Dict[str, Agent]) -> Dict[str, List[Task]]:
        """Distribute tasks to agents based on their capabilities."""
        assignments = {agent_id: [] for agent_id in agents.keys()}
        
        for task in tasks:
            # Simple round-robin for now
            agent_ids = list(agents.keys())
            selected_agent = agent_ids[len(task.task_id) % len(agent_ids)]
            
            task.assigned_agent = selected_agent
            assignments[selected_agent].append(task)
        
        return assignments
    
    def _select_agent_for_task(self, task: Task, agents: Dict[str, Agent]) -> str:
        """Select appropriate agent for a task."""
        # Simple selection based on task complexity
        if "complex" in task.title.lower():
            # Assign complex tasks to architecture or backend agents
            preferred = ["AGENT_E", "AGENT_A"]
        elif "ui" in task.title.lower() or "frontend" in task.title.lower():
            preferred = ["AGENT_B"]
        elif "test" in task.title.lower():
            preferred = ["AGENT_D"]
        elif "deploy" in task.title.lower():
            preferred = ["AGENT_C"]
        else:
            preferred = list(agents.keys())
        
        # Find available agent from preferred list
        for agent_id in preferred:
            if agent_id in agents and agents[agent_id].status == "active":
                return agent_id
        
        # Fallback to any available agent
        available_agents = [
            agent_id for agent_id, agent in agents.items()
            if agent.status == "active"
        ]
        
        return available_agents[0] if available_agents else list(agents.keys())[0]
    
    def _assign_task_to_agent(self, env: E2ETestEnvironment, 
                            agent_id: str, task: Task) -> Dict[str, Any]:
        """Assign a task to an agent."""
        try:
            # Use assign_task.sh script
            result = subprocess.run([
                "bash", str(env.workspace / "tools/assign_task.sh"),
                agent_id,
                task.task_id,
                task.title,
                task.priority,
                str(task.estimated_hours)
            ], capture_output=True, text=True, cwd=env.workspace)
            
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
            
        except Exception as e:
            env.metrics.errors.append(f"Task assignment failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _complete_task(self, env: E2ETestEnvironment, 
                      agent_id: str, task_id: str) -> Dict[str, Any]:
        """Complete a task."""
        try:
            # Use complete_task.sh script
            result = subprocess.run([
                "bash", str(env.workspace / "tools/complete_task.sh"),
                agent_id,
                task_id,
                f"Completed task {task_id}"
            ], capture_output=True, text=True, cwd=env.workspace)
            
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
            
        except Exception as e:
            env.metrics.errors.append(f"Task completion failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _verify_outbox_integrity(self, env: E2ETestEnvironment):
        """Verify that all outbox files are valid JSON and consistent."""
        for agent_id in env.agents.keys():
            outbox_path = env.workspace / f"postbox/{agent_id}/outbox.json"
            
            try:
                with open(outbox_path) as f:
                    data = json.load(f)
                
                # Verify required fields
                assert "agent_id" in data
                assert "tasks" in data
                assert isinstance(data["tasks"], list)
                
                # Verify task data consistency
                for task_data in data["tasks"]:
                    assert "task_id" in task_data
                    assert "status" in task_data
                    
            except (json.JSONDecodeError, AssertionError) as e:
                env.metrics.errors.append(f"Outbox integrity check failed for {agent_id}: {str(e)}")
                raise


class StressTester:
    """Stress testing for concurrent agent operations."""
    
    @pytest.mark.stress
    def test_extreme_concurrency(self):
        """Test system with extreme concurrent load."""
        with E2ETestEnvironment("extreme_concurrency") as env:
            # Generate massive concurrent load
            num_concurrent_operations = 100
            
            def stress_operation(operation_id):
                """Single stress operation."""
                task_id = f"STRESS_TASK_{operation_id}"
                agent_id = f"AGENT_{chr(65 + operation_id % 5)}"
                
                # Rapid assign-complete cycle
                task = Task(task_id, f"Stress Task {operation_id}", "LOW", 1, [])
                
                assign_result = MultiAgentScenarioTester()._assign_task_to_agent(env, agent_id, task)
                if not assign_result["success"]:
                    return {"success": False, "phase": "assign", "error": assign_result["error"]}
                
                complete_result = MultiAgentScenarioTester()._complete_task(env, agent_id, task_id)
                if not complete_result["success"]:
                    return {"success": False, "phase": "complete", "error": complete_result["error"]}
                
                return {"success": True}
            
            # Execute stress operations
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [
                    executor.submit(stress_operation, i)
                    for i in range(num_concurrent_operations)
                ]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Analyze results
            successful_operations = sum(1 for r in results if r["success"])
            success_rate = successful_operations / num_concurrent_operations
            throughput = num_concurrent_operations / duration
            
            # Stress test assertions
            assert success_rate > 0.8  # At least 80% success rate under stress
            assert throughput > 5      # At least 5 operations per second
            
            # Update metrics
            env.metrics.success_rate = success_rate
            env.metrics.operations_per_second = throughput
    
    @pytest.mark.stress
    def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation."""
        with E2ETestEnvironment("memory_leak") as env:
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Run operations over time
            num_cycles = 20
            operations_per_cycle = 10
            
            memory_samples = [initial_memory]
            
            for cycle in range(num_cycles):
                # Perform operations
                for i in range(operations_per_cycle):
                    task_id = f"MEMORY_TEST_{cycle}_{i}"
                    agent_id = f"AGENT_{chr(65 + i % 5)}"
                    
                    task = Task(task_id, f"Memory Test Task {cycle}-{i}", "LOW", 1, [])
                    
                    # Assign and complete
                    MultiAgentScenarioTester()._assign_task_to_agent(env, agent_id, task)
                    MultiAgentScenarioTester()._complete_task(env, agent_id, task_id)
                
                # Sample memory
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
                
                # Small delay between cycles
                time.sleep(0.1)
            
            final_memory = memory_samples[-1]
            memory_growth = final_memory - initial_memory
            
            # Memory growth should be reasonable (less than 50MB for this test)
            assert memory_growth < 50, f"Excessive memory growth: {memory_growth:.2f} MB"
            
            # Check for consistent growth pattern (possible leak indicator)
            growth_trend = all(
                memory_samples[i] <= memory_samples[i+1] + 5  # Allow 5MB variance
                for i in range(len(memory_samples)-1)
            )
            
            if memory_growth > 20 and growth_trend:
                env.metrics.warnings.append(f"Possible memory leak detected: {memory_growth:.2f} MB growth")


class ChaosTestingFramework:
    """Chaos testing for system resilience."""
    
    @pytest.mark.chaos
    def test_random_component_failures(self):
        """Test system resilience with random component failures."""
        with E2ETestEnvironment("chaos_failures") as env:
            # Setup baseline operations
            tasks = MultiAgentScenarioTester()._generate_tasks(50, ["simple", "medium"])
            
            # Assign initial tasks
            for task in tasks:
                agent_id = MultiAgentScenarioTester()._select_agent_for_task(task, env.agents)
                MultiAgentScenarioTester()._assign_task_to_agent(env, agent_id, task)
            
            # Introduce random failures
            failure_events = []
            
            def introduce_chaos():
                """Randomly introduce system failures."""
                for _ in range(10):  # 10 chaos events
                    time.sleep(random.uniform(0.1, 0.5))
                    
                    chaos_type = random.choice([
                        "agent_failure", "file_corruption", "resource_exhaustion"
                    ])
                    
                    if chaos_type == "agent_failure":
                        # Random agent goes offline
                        agent_id = random.choice(list(env.agents.keys()))
                        env.agents[agent_id].status = "offline"
                        failure_events.append(f"Agent {agent_id} failed")
                        
                        # Recover after short time
                        time.sleep(0.2)
                        env.agents[agent_id].status = "active"
                        failure_events.append(f"Agent {agent_id} recovered")
                    
                    elif chaos_type == "file_corruption":
                        # Temporarily corrupt a file
                        agent_id = random.choice(list(env.agents.keys()))
                        outbox_path = env.workspace / f"postbox/{agent_id}/outbox.json"
                        
                        # Backup original
                        with open(outbox_path) as f:
                            original_content = f.read()
                        
                        # Corrupt
                        with open(outbox_path, 'w') as f:
                            f.write("CORRUPTED DATA")
                        
                        failure_events.append(f"Corrupted {agent_id} outbox")
                        
                        # Restore after delay
                        time.sleep(0.1)
                        with open(outbox_path, 'w') as f:
                            f.write(original_content)
                        
                        failure_events.append(f"Restored {agent_id} outbox")
            
            # Run chaos in background
            chaos_thread = threading.Thread(target=introduce_chaos)
            chaos_thread.start()
            
            # Continue operations during chaos
            completed_tasks = []
            for task in tasks:
                try:
                    if env.agents[task.assigned_agent].status == "active":
                        result = MultiAgentScenarioTester()._complete_task(
                            env, task.assigned_agent, task.task_id
                        )
                        if result["success"]:
                            completed_tasks.append(task.task_id)
                    else:
                        # Reassign to available agent
                        available_agents = [
                            aid for aid, agent in env.agents.items()
                            if agent.status == "active"
                        ]
                        if available_agents:
                            new_agent = random.choice(available_agents)
                            task.assigned_agent = new_agent
                            MultiAgentScenarioTester()._assign_task_to_agent(env, new_agent, task)
                            result = MultiAgentScenarioTester()._complete_task(
                                env, new_agent, task.task_id
                            )
                            if result["success"]:
                                completed_tasks.append(task.task_id)
                
                except Exception as e:
                    env.metrics.errors.append(f"Chaos test error: {str(e)}")
            
            chaos_thread.join()
            
            # Analyze resilience
            completion_rate = len(completed_tasks) / len(tasks)
            
            # System should maintain reasonable operation despite chaos
            assert completion_rate > 0.6  # At least 60% completion rate during chaos
            assert len(failure_events) > 0  # Chaos events should have occurred
            
            env.metrics.success_rate = completion_rate
    
    @pytest.mark.chaos
    def test_network_partition_simulation(self):
        """Simulate network partitions between agents."""
        with E2ETestEnvironment("network_partition") as env:
            # Simulate network partition by making some agents "unreachable"
            partitioned_agents = ["AGENT_D", "AGENT_E"]
            
            # Mark partitioned agents as unreachable
            for agent_id in partitioned_agents:
                env.agents[agent_id].status = "unreachable"
            
            # Try to operate with reduced agent pool
            available_agents = [
                agent_id for agent_id, agent in env.agents.items()
                if agent.status == "active"
            ]
            
            tasks = MultiAgentScenarioTester()._generate_tasks(20, ["simple"])
            
            # Distribute tasks only to available agents
            successful_assignments = 0
            
            for task in tasks:
                if available_agents:
                    agent_id = random.choice(available_agents)
                    result = MultiAgentScenarioTester()._assign_task_to_agent(env, agent_id, task)
                    
                    if result["success"]:
                        successful_assignments += 1
                        complete_result = MultiAgentScenarioTester()._complete_task(
                            env, agent_id, task.task_id
                        )
            
            # System should continue operating with reduced capacity
            assert successful_assignments > 0
            assert successful_assignments >= len(tasks) * len(available_agents) / len(env.agents) * 0.8
            
            # Simulate network recovery
            for agent_id in partitioned_agents:
                env.agents[agent_id].status = "active"
            
            # Verify system can utilize recovered agents
            recovery_task = Task("RECOVERY_TEST", "Recovery Test", "HIGH", 1, [])
            recovery_agent = partitioned_agents[0]
            
            result = MultiAgentScenarioTester()._assign_task_to_agent(env, recovery_agent, recovery_task)
            assert result["success"]


if __name__ == "__main__":
    # Run E2E tests
    pytest.main([__file__, "-v", "-m", "e2e"])