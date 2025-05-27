"""
Unit tests for Parallel DAG Runner.

Tests the parallel execution capabilities of the DAG runner including
dependency resolution, concurrent execution, and error handling.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from services.workflow.dag_runner_parallel import (
    ParallelStatefulDAGRunner, ParallelDAGRunnerFactory
)
from services.workflow.dag_run_tracker import DAGStepStatus, DAGRunStatus
from services.workflow.dag_run_store import DAGRunStore


class TestParallelStatefulDAGRunner:
    """Test cases for ParallelStatefulDAGRunner."""
    
    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary DAGRunStore."""
        return DAGRunStore(storage_dir=str(tmp_path / "dag_runs"))
    
    @pytest.fixture
    def runner(self, store):
        """Create a ParallelStatefulDAGRunner instance."""
        return ParallelStatefulDAGRunner(
            dag_id="test-parallel-dag",
            store=store,
            max_concurrent_steps=3
        )
    
    @pytest.mark.asyncio
    async def test_parallel_execution_independent_steps(self, runner):
        """Test parallel execution of independent steps."""
        execution_order = []
        execution_times = {}
        
        async def create_step_executor(step_id: str, delay: float = 0.1):
            async def executor():
                execution_times[step_id] = datetime.utcnow()
                execution_order.append(f"{step_id}_start")
                await asyncio.sleep(delay)
                execution_order.append(f"{step_id}_end")
                return {"step": step_id, "result": "success"}
            return executor
        
        # Register independent steps
        runner.register_step("step1", await create_step_executor("step1", 0.2))
        runner.register_step("step2", await create_step_executor("step2", 0.1))
        runner.register_step("step3", await create_step_executor("step3", 0.15))
        
        # Execute DAG
        result = await runner.execute()
        
        # Verify all steps completed
        assert result.status == DAGRunStatus.SUCCESS
        assert all(
            step.status == DAGStepStatus.SUCCESS 
            for step in result.steps.values()
        )
        
        # Verify parallel execution - steps should start before others finish
        assert execution_order[0] in ["step1_start", "step2_start", "step3_start"]
        assert execution_order[1] in ["step1_start", "step2_start", "step3_start"]
        assert execution_order[2] in ["step1_start", "step2_start", "step3_start"]
        
        # Verify execution times are close (started roughly at the same time)
        times = list(execution_times.values())
        time_diffs = [
            (times[i] - times[0]).total_seconds() 
            for i in range(1, len(times))
        ]
        assert all(diff < 0.1 for diff in time_diffs), "Steps should start within 100ms of each other"
    
    @pytest.mark.asyncio
    async def test_dependency_resolution(self, runner):
        """Test that dependencies are respected during execution."""
        execution_order = []
        
        async def create_step_executor(step_id: str):
            async def executor():
                execution_order.append(step_id)
                await asyncio.sleep(0.05)
                return {"step": step_id}
            return executor
        
        # Register steps with dependencies
        # step1 and step2 are independent
        # step3 depends on step1
        # step4 depends on step2 and step3
        runner.register_step("step1", await create_step_executor("step1"))
        runner.register_step("step2", await create_step_executor("step2"))
        runner.register_step("step3", await create_step_executor("step3"), dependencies=["step1"])
        runner.register_step("step4", await create_step_executor("step4"), dependencies=["step2", "step3"])
        
        # Execute DAG
        result = await runner.execute()
        
        # Verify success
        assert result.status == DAGRunStatus.SUCCESS
        
        # Verify execution order respects dependencies
        step1_idx = execution_order.index("step1")
        step2_idx = execution_order.index("step2")
        step3_idx = execution_order.index("step3")
        step4_idx = execution_order.index("step4")
        
        # step3 must come after step1
        assert step3_idx > step1_idx
        
        # step4 must come after both step2 and step3
        assert step4_idx > step2_idx
        assert step4_idx > step3_idx
        
        # step1 and step2 can be in any order (parallel)
        # but both should be before step4
        assert step1_idx < step4_idx
        assert step2_idx < step4_idx
    
    @pytest.mark.asyncio
    async def test_max_concurrent_steps(self, runner):
        """Test that max_concurrent_steps limit is respected."""
        runner.max_concurrent_steps = 2  # Limit to 2 concurrent steps
        
        concurrent_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()
        
        async def create_step_executor(step_id: str):
            async def executor():
                nonlocal concurrent_count, max_concurrent
                
                async with lock:
                    concurrent_count += 1
                    max_concurrent = max(max_concurrent, concurrent_count)
                
                await asyncio.sleep(0.1)
                
                async with lock:
                    concurrent_count -= 1
                
                return {"step": step_id}
            return executor
        
        # Register 5 independent steps
        for i in range(5):
            runner.register_step(f"step{i}", await create_step_executor(f"step{i}"))
        
        # Execute DAG
        result = await runner.execute()
        
        # Verify success
        assert result.status == DAGRunStatus.SUCCESS
        
        # Verify max concurrent steps was respected
        assert max_concurrent <= 2, f"Max concurrent was {max_concurrent}, should be <= 2"
    
    @pytest.mark.asyncio
    async def test_dependency_failure_propagation(self, runner):
        """Test that dependent steps are skipped when dependency fails."""
        async def failing_step():
            raise Exception("Step failed!")
        
        async def successful_step():
            return {"result": "success"}
        
        # Register steps with dependencies
        runner.register_step("step1", failing_step, critical=False)
        runner.register_step("step2", successful_step)
        runner.register_step("step3", successful_step, dependencies=["step1"])
        runner.register_step("step4", successful_step, dependencies=["step3"])
        
        # Execute DAG
        result = await runner.execute()
        
        # Verify partial success (step1 failed but was non-critical)
        assert result.status == DAGRunStatus.PARTIAL_SUCCESS
        
        # Verify step statuses
        assert result.steps["step1"].status == DAGStepStatus.FAILED
        assert result.steps["step2"].status == DAGStepStatus.SUCCESS  # Independent step succeeded
        assert result.steps["step3"].status == DAGStepStatus.SKIPPED  # Skipped due to step1 failure
        assert result.steps["step4"].status == DAGStepStatus.SKIPPED  # Skipped due to step3 skip
    
    @pytest.mark.asyncio
    async def test_critical_failure_stops_dag(self, runner):
        """Test that critical step failure stops the entire DAG."""
        execution_order = []
        
        async def create_step_executor(step_id: str, should_fail: bool = False):
            async def executor():
                execution_order.append(step_id)
                if should_fail:
                    raise Exception(f"{step_id} failed!")
                return {"step": step_id}
            return executor
        
        # Register steps
        runner.register_step("step1", await create_step_executor("step1"))
        runner.register_step("step2", await create_step_executor("step2", should_fail=True), critical=True)
        runner.register_step("step3", await create_step_executor("step3"))
        runner.register_step("step4", await create_step_executor("step4"), dependencies=["step1"])
        
        # Execute DAG
        result = await runner.execute()
        
        # Verify failure
        assert result.status == DAGRunStatus.FAILED
        assert "Critical step 'step2' failed" in result.metadata.get('failure_reason', '')
        
        # Verify step2 failed
        assert result.steps["step2"].status == DAGStepStatus.FAILED
        
        # Some steps may have completed before the failure
        # but pending steps should be skipped
        for step_id, step in result.steps.items():
            if step_id not in execution_order and step_id != "step2":
                assert step.status == DAGStepStatus.SKIPPED
    
    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, runner):
        """Test detection of circular dependencies."""
        async def dummy_executor():
            return {"result": "success"}
        
        # Create circular dependency
        runner.register_step("step1", dummy_executor, dependencies=["step3"])
        runner.register_step("step2", dummy_executor, dependencies=["step1"])
        runner.register_step("step3", dummy_executor, dependencies=["step2"])
        
        # Validate dependencies
        errors = runner.validate_dependencies()
        
        assert len(errors) > 0
        assert any("Circular dependency" in error for error in errors)
    
    @pytest.mark.asyncio
    async def test_missing_dependency_validation(self, runner):
        """Test detection of missing dependencies."""
        async def dummy_executor():
            return {"result": "success"}
        
        # Register step with non-existent dependency
        runner.register_step("step1", dummy_executor, dependencies=["non_existent_step"])
        
        # Validate dependencies
        errors = runner.validate_dependencies()
        
        assert len(errors) == 1
        assert "non-existent step" in errors[0]
    
    @pytest.mark.asyncio
    async def test_complex_dependency_graph(self, runner):
        """Test execution of a complex dependency graph."""
        execution_order = []
        
        async def create_step_executor(step_id: str):
            async def executor():
                execution_order.append(step_id)
                await asyncio.sleep(0.01)
                return {"step": step_id}
            return executor
        
        # Create a diamond dependency pattern
        #     A
        #    / \
        #   B   C
        #    \ /
        #     D
        #     |
        #     E
        
        runner.register_step("A", await create_step_executor("A"))
        runner.register_step("B", await create_step_executor("B"), dependencies=["A"])
        runner.register_step("C", await create_step_executor("C"), dependencies=["A"])
        runner.register_step("D", await create_step_executor("D"), dependencies=["B", "C"])
        runner.register_step("E", await create_step_executor("E"), dependencies=["D"])
        
        # Execute DAG
        result = await runner.execute()
        
        # Verify success
        assert result.status == DAGRunStatus.SUCCESS
        
        # Verify execution order
        a_idx = execution_order.index("A")
        b_idx = execution_order.index("B")
        c_idx = execution_order.index("C")
        d_idx = execution_order.index("D")
        e_idx = execution_order.index("E")
        
        # A must be first
        assert a_idx == 0
        
        # B and C must come after A
        assert b_idx > a_idx
        assert c_idx > a_idx
        
        # D must come after both B and C
        assert d_idx > b_idx
        assert d_idx > c_idx
        
        # E must be last
        assert e_idx == len(execution_order) - 1
    
    @pytest.mark.asyncio
    async def test_resume_with_dependencies(self, runner, store):
        """Test resuming a DAG run maintains dependency information."""
        async def dummy_executor():
            return {"result": "success"}
        
        # Register steps with dependencies
        runner.register_step("step1", dummy_executor)
        runner.register_step("step2", dummy_executor, dependencies=["step1"])
        runner.register_step("step3", dummy_executor, dependencies=["step1", "step2"])
        
        # Get run ID
        run_id = runner.run_id
        
        # Create new runner to resume
        resumed_runner = ParallelDAGRunnerFactory.resume_runner(run_id, store)
        
        # Verify dependencies were restored
        assert resumed_runner._step_dependencies["step2"] == {"step1"}
        assert resumed_runner._step_dependencies["step3"] == {"step1", "step2"}
    
    @pytest.mark.asyncio
    async def test_get_dependency_graph(self, runner):
        """Test getting the dependency graph."""
        async def dummy_executor():
            return {"result": "success"}
        
        # Register steps with dependencies
        runner.register_step("step1", dummy_executor)
        runner.register_step("step2", dummy_executor, dependencies=["step1"])
        runner.register_step("step3", dummy_executor, dependencies=["step1", "step2"])
        
        # Get dependency graph
        graph = runner.get_dependency_graph()
        
        assert graph == {
            "step1": [],
            "step2": ["step1"],
            "step3": ["step1", "step2"]
        }


class TestParallelDAGRunnerFactory:
    """Test cases for ParallelDAGRunnerFactory."""
    
    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary DAGRunStore."""
        return DAGRunStore(storage_dir=str(tmp_path / "dag_runs"))
    
    def test_create_runner(self, store):
        """Test creating a new parallel runner."""
        runner = ParallelDAGRunnerFactory.create_runner(
            dag_id="test-dag",
            store=store,
            max_concurrent_steps=10
        )
        
        assert isinstance(runner, ParallelStatefulDAGRunner)
        assert runner.dag_id == "test-dag"
        assert runner.max_concurrent_steps == 10
        assert runner.dag_run.status == DAGRunStatus.CREATED
    
    @pytest.mark.asyncio
    async def test_resume_runner(self, store):
        """Test resuming an existing DAG run."""
        # Create and start a DAG
        runner1 = ParallelDAGRunnerFactory.create_runner("test-dag", store)
        
        async def dummy_executor():
            return {"result": "success"}
        
        runner1.register_step("step1", dummy_executor)
        runner1.register_step("step2", dummy_executor, dependencies=["step1"])
        
        run_id = runner1.run_id
        runner1.dag_run.start()
        runner1._persist_state()
        
        # Resume the DAG
        runner2 = ParallelDAGRunnerFactory.resume_runner(run_id, store)
        
        assert isinstance(runner2, ParallelStatefulDAGRunner)
        assert runner2.run_id == run_id
        assert runner2.dag_id == "test-dag"
        assert runner2.dag_run.status == DAGRunStatus.RUNNING
        
        # Verify dependencies were restored
        assert "step1" in runner2._step_dependencies
        assert runner2._step_dependencies["step2"] == {"step1"}