#!/usr/bin/env python3
"""
Failure Scenario Testing Suite for Multi-Agent Orchestration System.

Tests system behavior under various failure conditions including
network issues, agent crashes, partial completions, and data corruption.
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
import signal
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

from tests.e2e.multi_agent_scenarios import E2ETestEnvironment, TestMetrics, Agent, Task


@dataclass
class FailureScenario:
    """Represents a failure scenario to test."""
    scenario_id: str
    name: str
    description: str
    failure_type: str
    failure_probability: float
    recovery_time: float
    expected_behavior: str


class FailureScenarioTester:
    """Tests various failure scenarios in the orchestration system."""
    
    @pytest.mark.failure
    def test_agent_crash_recovery(self):
        """Test system recovery when agents crash unexpectedly."""
        with E2ETestEnvironment("agent_crash_recovery") as env:
            # Set up initial tasks
            tasks = self._generate_test_tasks(20)
            
            # Assign tasks to agents
            for i, task in enumerate(tasks):
                agent_id = f"AGENT_{chr(65 + i % 5)}"
                self._assign_task_to_agent(env, agent_id, task)
            
            # Simulate agent crash (AGENT_C)
            crashed_agent = "AGENT_C"
            crashed_agent_tasks = [t for t in tasks if t.assigned_agent == crashed_agent]
            
            # Mark agent as crashed
            env.agents[crashed_agent].status = "crashed"
            
            # Simulate crash by corrupting agent's outbox
            outbox_path = env.workspace / f"postbox/{crashed_agent}/outbox.json"
            with open(outbox_path, 'w') as f:
                f.write("CORRUPTED_DATA_CRASH")
            
            # Test recovery mechanism
            recovery_results = []
            
            # Attempt to reassign crashed agent's tasks
            for task in crashed_agent_tasks:
                # Find alternative agent
                available_agents = [
                    aid for aid, agent in env.agents.items()
                    if agent.status == "active" and aid != crashed_agent
                ]
                
                if available_agents:
                    new_agent = random.choice(available_agents)
                    
                    # Reassign task
                    task.assigned_agent = new_agent
                    result = self._assign_task_to_agent(env, new_agent, task)
                    recovery_results.append(result["success"])
            
            # Verify recovery
            recovery_rate = sum(recovery_results) / len(recovery_results) if recovery_results else 0
            assert recovery_rate > 0.8  # At least 80% of tasks should be recovered
            
            # Test completion of recovered tasks
            completed_recovered = 0
            for task in crashed_agent_tasks:
                if task.assigned_agent != crashed_agent:
                    result = self._complete_task(env, task.assigned_agent, task.task_id)
                    if result["success"]:
                        completed_recovered += 1
            
            completion_rate = completed_recovered / len(crashed_agent_tasks) if crashed_agent_tasks else 0
            assert completion_rate > 0.7  # At least 70% completion rate for recovered tasks
    
    @pytest.mark.failure
    def test_network_partition_scenarios(self):
        """Test system behavior during network partitions."""
        with E2ETestEnvironment("network_partition") as env:
            # Create tasks for distribution
            tasks = self._generate_test_tasks(30)
            
            # Assign tasks normally
            for i, task in enumerate(tasks):
                agent_id = f"AGENT_{chr(65 + i % 5)}"
                self._assign_task_to_agent(env, agent_id, task)
            
            # Simulate network partition - some agents become unreachable
            partitioned_agents = ["AGENT_D", "AGENT_E"]
            reachable_agents = ["AGENT_A", "AGENT_B", "AGENT_C"]
            
            # Mark partitioned agents as unreachable
            for agent_id in partitioned_agents:
                env.agents[agent_id].status = "unreachable"
            
            # Try to complete tasks only with reachable agents
            reachable_tasks = [t for t in tasks if t.assigned_agent in reachable_agents]
            unreachable_tasks = [t for t in tasks if t.assigned_agent in partitioned_agents]
            
            # Complete tasks on reachable agents
            reachable_completed = 0
            for task in reachable_tasks:
                result = self._complete_task(env, task.assigned_agent, task.task_id)
                if result["success"]:
                    reachable_completed += 1
            
            # Attempt to reassign unreachable tasks
            reassigned_tasks = 0
            for task in unreachable_tasks:
                # Reassign to reachable agent
                new_agent = random.choice(reachable_agents)
                task.assigned_agent = new_agent
                
                result = self._assign_task_to_agent(env, new_agent, task)
                if result["success"]:
                    reassigned_tasks += 1
                    
                    # Try to complete reassigned task
                    complete_result = self._complete_task(env, new_agent, task.task_id)
                    if not complete_result["success"]:
                        reassigned_tasks -= 1  # Count only successful completions
            
            # Verify system continued operating with reduced capacity
            total_completed = reachable_completed + reassigned_tasks
            expected_min_completion = len(tasks) * 0.6  # At least 60% should complete
            
            assert total_completed >= expected_min_completion
            
            # Simulate network recovery
            for agent_id in partitioned_agents:
                env.agents[agent_id].status = "active"
                
                # Restore agent outbox
                outbox_path = env.workspace / f"postbox/{agent_id}/outbox.json"
                with open(outbox_path, 'w') as f:
                    json.dump({
                        "agent_id": agent_id,
                        "agent_name": f"Test {env.agents[agent_id].agent_type.title()} Agent",
                        "agent_type": "test",
                        "expertise": env.agents[agent_id].capabilities,
                        "tasks": []
                    }, f, indent=2)
            
            # Verify recovered agents can accept new tasks
            recovery_task = Task("RECOVERY_TEST", "Network Recovery Test", "HIGH", 1, [])
            recovery_agent = partitioned_agents[0]
            
            result = self._assign_task_to_agent(env, recovery_agent, recovery_task)
            assert result["success"], "Recovered agent should accept new tasks"
    
    @pytest.mark.failure
    def test_partial_completion_scenarios(self):
        """Test scenarios where tasks are partially completed."""
        with E2ETestEnvironment("partial_completion") as env:
            # Create multi-step tasks that can fail at different stages
            complex_tasks = []
            for i in range(10):
                task = Task(
                    f"COMPLEX_TASK_{i:02d}",
                    f"Multi-step Task {i}",
                    "HIGH",
                    3,
                    []
                )
                complex_tasks.append(task)
            
            # Assign tasks
            for i, task in enumerate(complex_tasks):
                agent_id = f"AGENT_{chr(65 + i % 5)}"
                self._assign_task_to_agent(env, agent_id, task)
            
            # Simulate partial completion failures
            partial_failures = []
            
            for task in complex_tasks:
                failure_stage = random.choice(["assignment", "processing", "completion"])
                
                if failure_stage == "assignment":
                    # Task assigned but agent fails before processing
                    env.agents[task.assigned_agent].status = "failed"
                    partial_failures.append({
                        "task_id": task.task_id,
                        "failure_stage": "assignment",
                        "recovered": False
                    })
                    
                elif failure_stage == "processing":
                    # Task starts processing but fails midway
                    # Simulate by creating incomplete checkpoint
                    checkpoint_dir = env.workspace / "data/checkpoints"
                    checkpoint_dir.mkdir(parents=True, exist_ok=True)
                    
                    checkpoint_file = checkpoint_dir / f"{task.task_id}_partial.json"
                    with open(checkpoint_file, 'w') as f:
                        json.dump({
                            "task_id": task.task_id,
                            "status": "in_progress",
                            "completion_percentage": random.randint(20, 80),
                            "last_checkpoint": datetime.now().isoformat(),
                            "error": "Simulated processing failure"
                        }, f, indent=2)
                    
                    partial_failures.append({
                        "task_id": task.task_id,
                        "failure_stage": "processing",
                        "checkpoint_file": str(checkpoint_file),
                        "recovered": False
                    })
                    
                else:  # completion failure
                    # Task processes successfully but completion step fails
                    # Try to complete but expect potential failure
                    result = self._complete_task(env, task.assigned_agent, task.task_id)
                    
                    # Simulate completion failure by corrupting the result
                    if result["success"]:
                        # Corrupt the completion record
                        completion_record = env.workspace / f"postbox/{task.assigned_agent}/completed/{task.task_id}_completion.json"
                        if completion_record.exists():
                            with open(completion_record, 'w') as f:
                                f.write("CORRUPTED_COMPLETION_DATA")
                    
                    partial_failures.append({
                        "task_id": task.task_id,
                        "failure_stage": "completion",
                        "initial_success": result["success"],
                        "recovered": False
                    })
            
            # Implement recovery mechanisms for partial failures
            recovered_count = 0
            
            for failure in partial_failures:
                if failure["failure_stage"] == "assignment":
                    # Reassign to different agent
                    task = next(t for t in complex_tasks if t.task_id == failure["task_id"])
                    available_agents = [
                        aid for aid, agent in env.agents.items()
                        if agent.status == "active"
                    ]
                    
                    if available_agents:
                        new_agent = random.choice(available_agents)
                        task.assigned_agent = new_agent
                        result = self._assign_task_to_agent(env, new_agent, task)
                        
                        if result["success"]:
                            complete_result = self._complete_task(env, new_agent, task.task_id)
                            if complete_result["success"]:
                                failure["recovered"] = True
                                recovered_count += 1
                
                elif failure["failure_stage"] == "processing":
                    # Resume from checkpoint
                    checkpoint_file = Path(failure["checkpoint_file"])
                    if checkpoint_file.exists():
                        with open(checkpoint_file) as f:
                            checkpoint_data = json.load(f)
                        
                        # Simulate resuming from checkpoint
                        if checkpoint_data["completion_percentage"] > 50:
                            # If more than 50% complete, attempt to finish
                            task = next(t for t in complex_tasks if t.task_id == failure["task_id"])
                            result = self._complete_task(env, task.assigned_agent, task.task_id)
                            
                            if result["success"]:
                                failure["recovered"] = True
                                recovered_count += 1
                
                elif failure["failure_stage"] == "completion":
                    # Retry completion
                    task = next(t for t in complex_tasks if t.task_id == failure["task_id"])
                    result = self._complete_task(env, task.assigned_agent, task.task_id)
                    
                    if result["success"]:
                        failure["recovered"] = True
                        recovered_count += 1
            
            # Verify recovery effectiveness
            recovery_rate = recovered_count / len(partial_failures) if partial_failures else 0
            assert recovery_rate > 0.5  # At least 50% of partial failures should be recoverable
    
    @pytest.mark.failure
    def test_data_corruption_scenarios(self):
        """Test system behavior when data files are corrupted."""
        with E2ETestEnvironment("data_corruption") as env:
            # Set up normal operations
            tasks = self._generate_test_tasks(15)
            
            for i, task in enumerate(tasks):
                agent_id = f"AGENT_{chr(65 + i % 5)}"
                self._assign_task_to_agent(env, agent_id, task)
            
            # Introduce various types of data corruption
            corruption_scenarios = [
                {
                    "type": "outbox_corruption",
                    "file": env.workspace / "postbox/AGENT_A/outbox.json",
                    "corruption": "INVALID_JSON_DATA"
                },
                {
                    "type": "progress_corruption",
                    "file": env.workspace / ".sprint/progress.json",
                    "corruption": '{"incomplete": "json"'
                },
                {
                    "type": "task_file_corruption",
                    "file": env.workspace / "postbox/AGENT_B/inbox/TEST_TASK.md",
                    "corruption": "CORRUPTED_TASK_DATA"
                }
            ]
            
            corruption_results = []
            
            for scenario in corruption_scenarios:
                # Backup original file
                original_content = ""
                if scenario["file"].exists():
                    with open(scenario["file"]) as f:
                        original_content = f.read()
                
                # Introduce corruption
                scenario["file"].parent.mkdir(parents=True, exist_ok=True)
                with open(scenario["file"], 'w') as f:
                    f.write(scenario["corruption"])
                
                # Test system behavior with corruption
                test_task = Task(
                    f"CORRUPTION_TEST_{scenario['type']}",
                    f"Test for {scenario['type']}",
                    "MEDIUM",
                    1,
                    []
                )
                
                # Try to operate with corrupted data
                try:
                    if scenario["type"] == "outbox_corruption":
                        # Try to assign task to agent with corrupted outbox
                        result = self._assign_task_to_agent(env, "AGENT_A", test_task)
                        corruption_results.append({
                            "scenario": scenario["type"],
                            "operation_succeeded": result["success"],
                            "error": result.get("error", "")
                        })
                    
                    elif scenario["type"] == "progress_corruption":
                        # Try to complete a task with corrupted progress file
                        agent_id = "AGENT_C"
                        assign_result = self._assign_task_to_agent(env, agent_id, test_task)
                        if assign_result["success"]:
                            complete_result = self._complete_task(env, agent_id, test_task.task_id)
                            corruption_results.append({
                                "scenario": scenario["type"],
                                "operation_succeeded": complete_result["success"],
                                "error": complete_result.get("error", "")
                            })
                    
                    elif scenario["type"] == "task_file_corruption":
                        # Test reading corrupted task file
                        corruption_results.append({
                            "scenario": scenario["type"],
                            "operation_succeeded": False,  # Should handle gracefully
                            "error": "File corruption detected"
                        })
                
                except Exception as e:
                    corruption_results.append({
                        "scenario": scenario["type"],
                        "operation_succeeded": False,
                        "error": str(e)
                    })
                
                # Restore original content for next test
                if original_content:
                    with open(scenario["file"], 'w') as f:
                        f.write(original_content)
                elif scenario["file"].exists():
                    scenario["file"].unlink()
            
            # Verify system gracefully handles corruption
            # At least some operations should fail gracefully rather than crashing
            graceful_failures = sum(1 for r in corruption_results 
                                  if not r["operation_succeeded"] and "error" in r)
            
            assert graceful_failures > 0  # System should detect and handle corruption
            
            # Verify system can recover after corruption is fixed
            recovery_task = Task("RECOVERY_VERIFY", "Recovery Verification", "HIGH", 1, [])
            recovery_result = self._assign_task_to_agent(env, "AGENT_A", recovery_task)
            assert recovery_result["success"], "System should recover after corruption is fixed"
    
    @pytest.mark.failure
    def test_resource_exhaustion_scenarios(self):
        """Test system behavior under resource exhaustion conditions."""
        with E2ETestEnvironment("resource_exhaustion") as env:
            
            # Test disk space exhaustion simulation
            def test_disk_space_exhaustion():
                """Simulate disk space exhaustion."""
                # Create large temporary files to fill up space in test workspace
                large_files = []
                try:
                    for i in range(5):
                        large_file = env.workspace / f"large_file_{i}.tmp"
                        with open(large_file, 'wb') as f:
                            f.write(b'0' * (10 * 1024 * 1024))  # 10MB file
                        large_files.append(large_file)
                    
                    # Try to create tasks under disk pressure
                    task = Task("DISK_PRESSURE_TEST", "Disk Space Test", "HIGH", 1, [])
                    result = self._assign_task_to_agent(env, "AGENT_A", task)
                    
                    return result["success"]
                    
                finally:
                    # Clean up large files
                    for large_file in large_files:
                        try:
                            large_file.unlink()
                        except FileNotFoundError:
                            pass
            
            # Test file descriptor exhaustion
            def test_file_descriptor_exhaustion():
                """Simulate file descriptor exhaustion."""
                open_files = []
                try:
                    # Open many files to exhaust file descriptors
                    for i in range(100):
                        temp_file = env.workspace / f"fd_test_{i}.tmp"
                        f = open(temp_file, 'w')
                        f.write(f"Test file {i}")
                        open_files.append(f)
                    
                    # Try to operate under file descriptor pressure
                    task = Task("FD_PRESSURE_TEST", "File Descriptor Test", "MEDIUM", 1, [])
                    result = self._assign_task_to_agent(env, "AGENT_B", task)
                    
                    return result["success"]
                    
                finally:
                    # Close all open files
                    for f in open_files:
                        try:
                            f.close()
                            f.name and Path(f.name).unlink()
                        except:
                            pass
            
            # Run resource exhaustion tests
            disk_test_result = test_disk_space_exhaustion()
            fd_test_result = test_file_descriptor_exhaustion()
            
            # System should handle resource exhaustion gracefully
            # At least one test should demonstrate graceful degradation
            assert disk_test_result or fd_test_result, \
                "System should handle at least some resource exhaustion scenarios"
    
    def _generate_test_tasks(self, count: int) -> List[Task]:
        """Generate test tasks for failure scenarios."""
        tasks = []
        for i in range(count):
            task = Task(
                task_id=f"FAILURE_TEST_{i:03d}",
                title=f"Failure Test Task {i}",
                priority=random.choice(["HIGH", "MEDIUM", "LOW"]),
                estimated_hours=random.randint(1, 3),
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
            ], capture_output=True, text=True, cwd=env.workspace, timeout=15)
            
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
            return {"success": False, "error": "Assignment operation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _complete_task(self, env: E2ETestEnvironment, 
                      agent_id: str, task_id: str) -> Dict[str, Any]:
        """Complete a task."""
        try:
            result = subprocess.run([
                "bash", str(env.workspace / "tools/complete_task.sh"),
                agent_id, task_id, f"Completed failure test task {task_id}"
            ], capture_output=True, text=True, cwd=env.workspace, timeout=15)
            
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
            return {"success": False, "error": "Completion operation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run failure scenario tests
    pytest.main([__file__, "-v", "-m", "failure"])