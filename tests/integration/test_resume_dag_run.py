"""
Integration tests for DAG resume functionality.

These tests simulate DAG failures and verify that runs can be
successfully resumed from their last valid state.
"""

import asyncio
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from services.workflow.dag_runner import StatefulDAGRunner, DAGRunnerFactory
from services.workflow.dag_run_store import DAGRunStore
from services.workflow.dag_resume_manager import DAGResumeManager
from services.workflow.dag_run_tracker import DAGRunStatus, DAGStepStatus


class TestDAGResume(unittest.TestCase):
    """Integration tests for DAG resume functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = DAGRunStore(storage_path=self.temp_dir)
        self.resume_manager = DAGResumeManager(store=self.store)
        
        # Track execution for testing
        self.execution_log = []
        self.fail_on_step = None
        self.fail_count = 0
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    async def mock_step_executor(self, step_id: str):
        """Mock step executor that can simulate failures."""
        self.execution_log.append(f"Executing {step_id}")
        
        # Simulate failure if configured
        if self.fail_on_step == step_id and self.fail_count > 0:
            self.fail_count -= 1
            raise Exception(f"Simulated failure in {step_id}")
        
        # Return success result
        return f"Result from {step_id}"
    
    def test_resume_after_failure(self):
        """Test resuming a DAG after a step failure."""
        asyncio.run(self._test_resume_after_failure())
    
    async def _test_resume_after_failure(self):
        """Async test for resume after failure."""
        # Create initial DAG runner
        runner = DAGRunnerFactory.create_runner("test_dag", store=self.store)
        
        # Register steps
        runner.register_step("step1", lambda: self.mock_step_executor("step1"), max_retries=0)
        runner.register_step("step2", lambda: self.mock_step_executor("step2"), max_retries=0)
        runner.register_step("step3", lambda: self.mock_step_executor("step3"), max_retries=0)
        
        # Configure to fail on step2
        self.fail_on_step = "step2"
        self.fail_count = 1
        
        # Execute DAG - should fail on step2
        try:
            await runner.execute(["step1", "step2", "step3"])
        except Exception:
            pass  # Expected failure
        
        # Verify state
        run_id = runner.run_id
        dag_run = self.store.get(run_id)
        self.assertEqual(dag_run.status, DAGRunStatus.FAILED)
        self.assertEqual(dag_run.steps["step1"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(dag_run.steps["step2"].status, DAGStepStatus.FAILED)
        self.assertEqual(dag_run.steps["step3"].status, DAGStepStatus.SKIPPED)
        
        # Verify execution log
        self.assertEqual(self.execution_log, ["Executing step1", "Executing step2"])
        
        # Check if run can be resumed
        can_resume, reason = self.resume_manager.can_resume(run_id)
        self.assertTrue(can_resume)
        
        # Get resume state
        resume_state = self.resume_manager.get_resume_state(run_id)
        self.assertEqual(resume_state['completed_steps'], ["step1"])
        self.assertEqual(resume_state['failed_steps'], ["step2"])
        self.assertEqual(resume_state['skipped_steps'], ["step3"])
        
        # Clear execution log and disable failure
        self.execution_log.clear()
        self.fail_on_step = None
        
        # Resume the DAG
        resumed_runner = DAGRunnerFactory.resume_runner(run_id, store=self.store)
        
        # Re-register steps (in real use case, this would be done by the orchestrator)
        resumed_runner.register_step("step1", lambda: self.mock_step_executor("step1"), max_retries=0)
        resumed_runner.register_step("step2", lambda: self.mock_step_executor("step2"), max_retries=0)
        resumed_runner.register_step("step3", lambda: self.mock_step_executor("step3"), max_retries=0)
        
        # Execute resumed DAG
        await resumed_runner.execute(["step1", "step2", "step3"])
        
        # Verify final state
        final_dag_run = self.store.get(run_id)
        self.assertEqual(final_dag_run.status, DAGRunStatus.SUCCESS)
        self.assertEqual(final_dag_run.steps["step1"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(final_dag_run.steps["step2"].status, DAGStepStatus.SUCCESS)
        self.assertEqual(final_dag_run.steps["step3"].status, DAGStepStatus.SUCCESS)
        
        # Verify only failed and pending steps were re-executed
        self.assertEqual(self.execution_log, ["Executing step2", "Executing step3"])
        
        # Verify resume metadata was added
        self.assertIn('resumed_at', final_dag_run.metadata)
        self.assertEqual(final_dag_run.metadata['resume_count'], 1)
    
    def test_resume_with_retries(self):
        """Test resuming a DAG with retry logic."""
        asyncio.run(self._test_resume_with_retries())
    
    async def _test_resume_with_retries(self):
        """Async test for resume with retries."""
        # Create initial DAG runner
        runner = DAGRunnerFactory.create_runner("test_dag_retry", store=self.store)
        
        # Register steps with retries
        runner.register_step("step1", lambda: self.mock_step_executor("step1"), max_retries=2)
        runner.register_step("step2", lambda: self.mock_step_executor("step2"), max_retries=2)
        
        # Configure to fail on step2 multiple times
        self.fail_on_step = "step2"
        self.fail_count = 3  # Will exhaust retries
        
        # Execute DAG - should fail after retries
        try:
            await runner.execute(["step1", "step2"])
        except Exception:
            pass  # Expected failure
        
        # Verify state
        run_id = runner.run_id
        dag_run = self.store.get(run_id)
        self.assertEqual(dag_run.status, DAGRunStatus.FAILED)
        self.assertEqual(dag_run.steps["step2"].retry_count, 2)  # Used all retries
        
        # Clear execution log and disable failure
        self.execution_log.clear()
        self.fail_count = 0  # No more failures
        
        # Resume the DAG
        resumed_runner = DAGRunnerFactory.resume_runner(run_id, store=self.store)
        
        # Re-register steps
        resumed_runner.register_step("step1", lambda: self.mock_step_executor("step1"), max_retries=2)
        resumed_runner.register_step("step2", lambda: self.mock_step_executor("step2"), max_retries=2)
        
        # Execute resumed DAG - should succeed this time
        await resumed_runner.execute(["step1", "step2"])
        
        # Verify final state
        final_dag_run = self.store.get(run_id)
        self.assertEqual(final_dag_run.status, DAGRunStatus.SUCCESS)
        
        # Verify execution included retry
        self.assertIn("Executing step2", self.execution_log)
    
    def test_cannot_resume_successful_dag(self):
        """Test that successful DAGs cannot be resumed."""
        asyncio.run(self._test_cannot_resume_successful_dag())
    
    async def _test_cannot_resume_successful_dag(self):
        """Async test for non-resumable successful DAG."""
        # Create and execute successful DAG
        runner = DAGRunnerFactory.create_runner("test_dag_success", store=self.store)
        runner.register_step("step1", lambda: self.mock_step_executor("step1"))
        
        await runner.execute(["step1"])
        
        # Verify cannot resume
        run_id = runner.run_id
        can_resume, reason = self.resume_manager.can_resume(run_id)
        self.assertFalse(can_resume)
        self.assertIn("already completed successfully", reason)
    
    def test_resume_statistics(self):
        """Test resume statistics functionality."""
        asyncio.run(self._test_resume_statistics())
    
    async def _test_resume_statistics(self):
        """Async test for resume statistics."""
        # Create multiple DAG runs with different states
        
        # Successful run
        runner1 = DAGRunnerFactory.create_runner("dag1", store=self.store)
        runner1.register_step("step1", lambda: self.mock_step_executor("step1"))
        await runner1.execute(["step1"])
        
        # Failed run
        self.fail_on_step = "step1"
        self.fail_count = 1
        runner2 = DAGRunnerFactory.create_runner("dag2", store=self.store)
        runner2.register_step("step1", lambda: self.mock_step_executor("step1"), max_retries=0)
        try:
            await runner2.execute(["step1"])
        except Exception:
            pass
        
        # Get statistics
        stats = self.resume_manager.get_resume_statistics()
        
        # Verify statistics
        self.assertEqual(stats['total_runs'], 2)
        self.assertEqual(stats['resumable_runs'], 1)
        self.assertEqual(stats['failed_runs'], 1)
        self.assertEqual(len(stats['resume_candidates']), 1)
        self.assertEqual(stats['resume_candidates'][0]['dag_id'], 'dag2')


if __name__ == "__main__":
    unittest.main()