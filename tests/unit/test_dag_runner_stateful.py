"""
Unit tests for stateful DAG runner.
"""

import unittest
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch
import time

from services.workflow.dag_runner import StatefulDAGRunner, DAGRunnerFactory, RetryBackoffStrategy
from services.workflow.dag_run_tracker import DAGRunStatus, DAGStepStatus
from services.workflow.dag_run_store import DAGRunStore


class TestStatefulDAGRunner(unittest.TestCase):
    """Test cases for StatefulDAGRunner."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = DAGRunStore(storage_path=self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_runner_creation(self):
        """Test creating a new DAG runner."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        self.assertEqual(runner.dag_id, "test_dag")
        self.assertIsNotNone(runner.run_id)
        self.assertEqual(runner.dag_run.status, DAGRunStatus.CREATED)
        
        # Verify run was persisted
        stored_run = self.store.get(runner.run_id)
        self.assertIsNotNone(stored_run)
        self.assertEqual(stored_run.dag_id, "test_dag")
    
    def test_runner_resume(self):
        """Test resuming an existing DAG run."""
        # Create initial run
        runner1 = StatefulDAGRunner("test_dag", self.store)
        run_id = runner1.run_id
        runner1.register_step("step1", AsyncMock())
        
        # Resume the run
        runner2 = StatefulDAGRunner("test_dag", self.store, run_id=run_id)
        
        self.assertEqual(runner2.run_id, run_id)
        self.assertEqual(runner2.dag_id, "test_dag")
        self.assertIn("step1", runner2.dag_run.steps)
    
    def test_step_registration(self):
        """Test registering step executors."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        mock_executor = AsyncMock()
        runner.register_step("step1", mock_executor, max_retries=5)
        
        self.assertIn("step1", runner._step_executors)
        self.assertIn("step1", runner.dag_run.steps)
        self.assertEqual(runner.dag_run.steps["step1"].max_retries, 5)
    
    async def test_successful_execution(self):
        """Test successful DAG execution."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Register steps
        step1_result = {"output": "step1_done"}
        step2_result = {"output": "step2_done"}
        
        step1_executor = AsyncMock(return_value=step1_result)
        step2_executor = AsyncMock(return_value=step2_result)
        
        runner.register_step("step1", step1_executor)
        runner.register_step("step2", step2_executor)
        
        # Execute
        result = await runner.execute()
        
        # Verify execution
        self.assertEqual(result.status, DAGRunStatus.SUCCESS)
        self.assertEqual(result.steps["step1"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(result.steps["step1"].result, step1_result)
        self.assertEqual(result.steps["step2"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(result.steps["step2"].result, step2_result)
        
        # Verify executors were called
        step1_executor.assert_called_once()
        step2_executor.assert_called_once()
    
    async def test_step_failure_with_retry(self):
        """Test step failure and retry logic."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Create executor that fails twice then succeeds
        call_count = 0
        
        async def flaky_executor():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Failure {call_count}")
            return {"output": "success"}
        
        runner.register_step("flaky_step", flaky_executor, max_retries=3)
        
        # Execute
        result = await runner.execute()
        
        # Verify retry behavior
        self.assertEqual(result.status, DAGRunStatus.SUCCESS)
        self.assertEqual(result.steps["flaky_step"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(result.steps["flaky_step"].retry_count, 2)
        self.assertEqual(call_count, 3)
    
    async def test_step_failure_exhausted_retries(self):
        """Test step failure after exhausting retries."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Always failing executor
        failing_executor = AsyncMock(side_effect=Exception("Always fails"))
        
        runner.register_step("failing_step", failing_executor, max_retries=2)
        
        # Execute - the runner doesn't re-raise exceptions for failed steps
        await runner.execute()
        
        # Verify failure
        self.assertEqual(runner.dag_run.status, DAGRunStatus.FAILED)
        self.assertEqual(runner.dag_run.steps["failing_step"].status, DAGStepStatus.FAILED)
        self.assertEqual(runner.dag_run.steps["failing_step"].retry_count, 2)
        self.assertEqual(failing_executor.call_count, 3)  # Initial + 2 retries
    
    async def test_resume_partial_completion(self):
        """Test resuming a partially completed DAG."""
        # Create initial run with 3 steps
        runner1 = StatefulDAGRunner("test_dag", self.store)
        run_id = runner1.run_id
        
        step1_executor = AsyncMock(return_value={"output": "step1"})
        step2_executor = AsyncMock(side_effect=Exception("Step 2 fails"))
        step3_executor = AsyncMock(return_value={"output": "step3"})
        
        runner1.register_step("step1", step1_executor)
        runner1.register_step("step2", step2_executor, max_retries=0)
        runner1.register_step("step3", step3_executor)
        
        # Execute and fail at step2
        await runner1.execute()
        
        # Verify partial completion
        self.assertEqual(runner1.dag_run.steps["step1"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(runner1.dag_run.steps["step2"].status, DAGStepStatus.FAILED)
        self.assertEqual(runner1.dag_run.steps["step3"].status, DAGStepStatus.SKIPPED)
        
        # Resume with fixed step2
        runner2 = StatefulDAGRunner("test_dag", self.store, run_id=run_id)
        
        # Re-register with working executors
        step1_executor_new = AsyncMock(return_value={"output": "step1"})
        step2_executor_new = AsyncMock(return_value={"output": "step2_fixed"})
        step3_executor_new = AsyncMock(return_value={"output": "step3"})
        
        runner2.register_step("step1", step1_executor_new)
        runner2.register_step("step2", step2_executor_new)
        runner2.register_step("step3", step3_executor_new)
        
        # Mark step2 as pending to retry it and reset DAG status
        runner2.dag_run.steps["step2"].status = DAGStepStatus.PENDING
        runner2.dag_run.steps["step3"].status = DAGStepStatus.PENDING
        runner2.dag_run.status = DAGRunStatus.RUNNING
        
        # Execute resumed run
        await runner2.execute()
        
        # Step1 should not be re-executed (already success)
        step1_executor_new.assert_not_called()
        
        # Step2 and step3 should be executed
        step2_executor_new.assert_called_once()
        step3_executor_new.assert_called_once()
        
        # Verify final state
        self.assertEqual(runner2.dag_run.status, DAGRunStatus.SUCCESS)
        self.assertEqual(runner2.dag_run.steps["step2"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(runner2.dag_run.steps["step3"].status, DAGStepStatus.SUCCESS)
    
    async def test_cancel_dag_run(self):
        """Test cancelling a DAG run."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Register steps
        runner.register_step("step1", AsyncMock())
        runner.register_step("step2", AsyncMock())
        
        # Cancel
        await runner.cancel()
        
        # Verify cancellation
        self.assertEqual(runner.dag_run.status, DAGRunStatus.CANCELLED)
        self.assertEqual(runner.dag_run.steps["step1"].status, DAGStepStatus.CANCELLED)
        self.assertEqual(runner.dag_run.steps["step2"].status, DAGStepStatus.CANCELLED)
    
    async def test_custom_step_order(self):
        """Test executing steps in custom order."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        execution_order = []
        
        async def track_execution(step_name):
            execution_order.append(step_name)
            return {"step": step_name}
        
        runner.register_step("step1", lambda: track_execution("step1"))
        runner.register_step("step2", lambda: track_execution("step2"))
        runner.register_step("step3", lambda: track_execution("step3"))
        
        # Execute in custom order
        await runner.execute(step_order=["step3", "step1", "step2"])
        
        # Verify execution order
        self.assertEqual(execution_order, ["step3", "step1", "step2"])
    
    def test_get_status(self):
        """Test getting DAG run status."""
        runner = StatefulDAGRunner("test_dag", self.store)
        runner.register_step("step1", AsyncMock())
        
        status = runner.get_status()
        
        self.assertEqual(status["run_id"], runner.run_id)
        self.assertEqual(status["dag_id"], "test_dag")
        self.assertEqual(status["status"], "created")
        self.assertIn("summary", status)
        self.assertIn("steps", status)
        self.assertIn("step1", status["steps"])
    
    async def test_critical_vs_non_critical_steps(self):
        """Test handling of critical vs non-critical step failures."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Register non-critical failing step
        failing_executor = AsyncMock(side_effect=Exception("Non-critical failure"))
        runner.register_step("non_critical", failing_executor, max_retries=0)
        runner.dag_run.steps["non_critical"].metadata["critical"] = False
        
        # Register subsequent step
        success_executor = AsyncMock(return_value={"output": "success"})
        runner.register_step("next_step", success_executor)
        
        # Execute
        result = await runner.execute()
        
        # Non-critical failure shouldn't stop execution
        self.assertEqual(result.status, DAGRunStatus.PARTIAL_SUCCESS)
        self.assertEqual(result.steps["non_critical"].status, DAGStepStatus.FAILED)
        self.assertEqual(result.steps["next_step"].status, DAGStepStatus.SUCCESS)
        
        # Next step should have been executed
        success_executor.assert_called_once()
    
    async def test_configurable_retry_delay(self):
        """Test configurable retry delay with different backoff strategies."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Track execution times
        execution_times = []
        
        async def timing_executor():
            execution_times.append(time.time())
            if len(execution_times) < 3:
                raise Exception("Test failure")
            return {"output": "success"}
        
        # Test exponential backoff
        runner.register_step("exp_step", timing_executor, 
                           max_retries=3, 
                           retry_delay=0.1,
                           retry_backoff=RetryBackoffStrategy.EXPONENTIAL)
        
        await runner.execute()
        
        # Check retry delays (should be ~0.1s, ~0.2s)
        self.assertEqual(len(execution_times), 3)
        delay1 = execution_times[1] - execution_times[0]
        delay2 = execution_times[2] - execution_times[1]
        
        self.assertAlmostEqual(delay1, 0.1, delta=0.05)
        self.assertAlmostEqual(delay2, 0.2, delta=0.05)
    
    async def test_linear_backoff_strategy(self):
        """Test linear backoff retry strategy."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        execution_times = []
        
        async def timing_executor():
            execution_times.append(time.time())
            if len(execution_times) < 3:
                raise Exception("Test failure")
            return {"output": "success"}
        
        runner.register_step("linear_step", timing_executor,
                           max_retries=3,
                           retry_delay=0.1,
                           retry_backoff=RetryBackoffStrategy.LINEAR)
        
        await runner.execute()
        
        # Check linear delays (should be ~0.1s, ~0.2s)
        delay1 = execution_times[1] - execution_times[0]
        delay2 = execution_times[2] - execution_times[1]
        
        self.assertAlmostEqual(delay1, 0.1, delta=0.05)
        self.assertAlmostEqual(delay2, 0.2, delta=0.05)
    
    async def test_constant_backoff_strategy(self):
        """Test constant backoff retry strategy."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        execution_times = []
        
        async def timing_executor():
            execution_times.append(time.time())
            if len(execution_times) < 3:
                raise Exception("Test failure")
            return {"output": "success"}
        
        runner.register_step("const_step", timing_executor,
                           max_retries=3,
                           retry_delay=0.1,
                           retry_backoff=RetryBackoffStrategy.CONSTANT)
        
        await runner.execute()
        
        # Check constant delays (should both be ~0.1s)
        delay1 = execution_times[1] - execution_times[0]
        delay2 = execution_times[2] - execution_times[1]
        
        self.assertAlmostEqual(delay1, 0.1, delta=0.05)
        self.assertAlmostEqual(delay2, 0.1, delta=0.05)
    
    async def test_error_logging_in_metadata(self):
        """Test that errors are logged in step and DAG metadata."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Executor that fails with specific error
        error_executor = AsyncMock(side_effect=ValueError("Specific test error"))
        
        runner.register_step("error_step", error_executor, max_retries=2)
        
        # Execute and expect failure
        await runner.execute()
        
        # Check step metadata
        step = runner.dag_run.steps["error_step"]
        self.assertIn('error_history', step.metadata)
        self.assertEqual(len(step.metadata['error_history']), 3)  # Initial + 2 retries
        
        # Check each error entry
        for i, error_entry in enumerate(step.metadata['error_history']):
            self.assertEqual(error_entry['attempt'], i + 1)
            self.assertEqual(error_entry['error'], "Specific test error")
            self.assertEqual(error_entry['error_type'], "ValueError")
            self.assertIn('timestamp', error_entry)
        
        # Check DAG metadata
        self.assertIn('step_failures', runner.dag_run.metadata)
        self.assertEqual(len(runner.dag_run.metadata['step_failures']), 1)
        
        failure_entry = runner.dag_run.metadata['step_failures'][0]
        self.assertEqual(failure_entry['step_id'], 'error_step')
        self.assertEqual(failure_entry['attempts'], 3)
        self.assertEqual(failure_entry['final_error'], "Specific test error")
        self.assertTrue(failure_entry['critical'])
        
        # Check failure reason
        self.assertIn('failure_reason', runner.dag_run.metadata)
        self.assertIn("Critical step 'error_step' failed", runner.dag_run.metadata['failure_reason'])
    
    async def test_non_critical_step_allows_continuation(self):
        """Test that non-critical step failures don't stop DAG execution."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Register steps
        success1 = AsyncMock(return_value={"output": "step1"})
        failing_non_critical = AsyncMock(side_effect=Exception("Non-critical failure"))
        success2 = AsyncMock(return_value={"output": "step2"})
        
        runner.register_step("step1", success1)
        runner.register_step("non_critical", failing_non_critical, 
                           max_retries=0, 
                           critical=False)
        runner.register_step("step2", success2)
        
        # Execute
        result = await runner.execute()
        
        # Verify execution continued after non-critical failure
        success1.assert_called_once()
        failing_non_critical.assert_called_once()
        success2.assert_called_once()
        
        # Check status
        self.assertEqual(result.status, DAGRunStatus.PARTIAL_SUCCESS)
        self.assertEqual(result.steps["step1"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(result.steps["non_critical"].status, DAGStepStatus.FAILED)
        self.assertEqual(result.steps["step2"].status, DAGStepStatus.SUCCESS)
    
    async def test_retry_parameter_override(self):
        """Test that retry parameters can be overridden per step."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Register two steps with different retry configs
        fast_retry = AsyncMock(side_effect=[Exception("Fail1"), {"output": "success"}])
        slow_retry = AsyncMock(side_effect=[Exception("Fail2"), {"output": "success"}])
        
        runner.register_step("fast", fast_retry, 
                           max_retries=1, 
                           retry_delay=0.05,
                           retry_backoff=RetryBackoffStrategy.CONSTANT)
        
        runner.register_step("slow", slow_retry,
                           max_retries=1,
                           retry_delay=0.15,
                           retry_backoff=RetryBackoffStrategy.CONSTANT)
        
        start_time = time.time()
        await runner.execute()
        total_time = time.time() - start_time
        
        # Fast retry should take ~0.05s, slow retry ~0.15s
        # Total should be at least 0.2s but less than 0.4s
        self.assertGreater(total_time, 0.15)
        self.assertLess(total_time, 0.4)
        
        # Both should succeed after retry
        self.assertEqual(runner.dag_run.status, DAGRunStatus.SUCCESS)
        self.assertEqual(runner.dag_run.steps["fast"].retry_count, 1)
        self.assertEqual(runner.dag_run.steps["slow"].retry_count, 1)
    
    async def test_dag_level_error_logging(self):
        """Test that DAG-level errors are logged in metadata."""
        runner = StatefulDAGRunner("test_dag", self.store)
        
        # Mock execute to raise an unexpected error
        with patch.object(runner, '_execute_step', side_effect=RuntimeError("Unexpected DAG error")):
            runner.register_step("step1", AsyncMock())
            
            with self.assertRaises(RuntimeError):
                await runner.execute()
            
            # Check DAG metadata for error
            self.assertIn('errors', runner.dag_run.metadata)
            self.assertEqual(len(runner.dag_run.metadata['errors']), 1)
            
            error_entry = runner.dag_run.metadata['errors'][0]
            self.assertEqual(error_entry['type'], 'dag_execution_error')
            self.assertEqual(error_entry['error'], "Unexpected DAG error")
            self.assertEqual(error_entry['error_type'], "RuntimeError")
            self.assertIn('timestamp', error_entry)


class TestDAGRunnerFactory(unittest.TestCase):
    """Test cases for DAGRunnerFactory."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = DAGRunStore(storage_path=self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_runner(self):
        """Test creating a new runner via factory."""
        runner = DAGRunnerFactory.create_runner("test_dag", self.store)
        
        self.assertIsInstance(runner, StatefulDAGRunner)
        self.assertEqual(runner.dag_id, "test_dag")
        self.assertIsNotNone(runner.run_id)
    
    def test_resume_runner(self):
        """Test resuming a runner via factory."""
        # Create initial run
        runner1 = DAGRunnerFactory.create_runner("test_dag", self.store)
        run_id = runner1.run_id
        
        # Resume
        runner2 = DAGRunnerFactory.resume_runner(run_id, self.store)
        
        self.assertIsInstance(runner2, StatefulDAGRunner)
        self.assertEqual(runner2.run_id, run_id)
        self.assertEqual(runner2.dag_id, "test_dag")
    
    def test_resume_nonexistent_run(self):
        """Test resuming a non-existent run."""
        with self.assertRaises(ValueError) as context:
            DAGRunnerFactory.resume_runner("nonexistent", self.store)
        
        self.assertIn("not found", str(context.exception))


def async_test(coro):
    """Decorator to run async tests."""
    def wrapper(self):
        asyncio.run(coro(self))
    return wrapper


# Apply async decorator to all async test methods
for attr_name in dir(TestStatefulDAGRunner):
    attr = getattr(TestStatefulDAGRunner, attr_name)
    if asyncio.iscoroutinefunction(attr):
        setattr(TestStatefulDAGRunner, attr_name, async_test(attr))


if __name__ == '__main__':
    unittest.main()
