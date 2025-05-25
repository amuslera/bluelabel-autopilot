"""
Unit tests for DAGRun state tracker.
"""

import unittest
from datetime import datetime, timedelta
import tempfile
import shutil
from pathlib import Path

from services.workflow.dag_run_tracker import (
    DAGRun, DAGStepState, DAGStepStatus, DAGRunStatus
)
from services.workflow.dag_run_store import DAGRunStore
from shared.schemas.dag_run_schema import validate_dag_run, validate_dag_step_state


class TestDAGStepState(unittest.TestCase):
    """Test cases for DAGStepState."""
    
    def test_step_creation(self):
        """Test creating a new step."""
        step = DAGStepState(step_id="test_step")
        self.assertEqual(step.step_id, "test_step")
        self.assertEqual(step.status, DAGStepStatus.PENDING)
        self.assertIsNone(step.start_time)
        self.assertIsNone(step.end_time)
        self.assertEqual(step.retry_count, 0)
        self.assertEqual(step.max_retries, 3)
    
    def test_step_start(self):
        """Test starting a step."""
        step = DAGStepState(step_id="test_step")
        step.start()
        
        self.assertEqual(step.status, DAGStepStatus.RUNNING)
        self.assertIsNotNone(step.start_time)
        self.assertIsInstance(step.start_time, datetime)
    
    def test_step_complete(self):
        """Test completing a step successfully."""
        step = DAGStepState(step_id="test_step")
        step.start()
        result = {"output": "test_result"}
        step.complete(result)
        
        self.assertEqual(step.status, DAGStepStatus.SUCCESS)
        self.assertIsNotNone(step.end_time)
        self.assertEqual(step.result, result)
        self.assertIsNotNone(step.duration_seconds)
    
    def test_step_fail(self):
        """Test failing a step."""
        step = DAGStepState(step_id="test_step")
        step.start()
        step.fail("Test error message")
        
        self.assertEqual(step.status, DAGStepStatus.FAILED)
        self.assertIsNotNone(step.end_time)
        self.assertEqual(step.error, "Test error message")
    
    def test_step_retry(self):
        """Test retrying a step."""
        step = DAGStepState(step_id="test_step", max_retries=2)
        step.start()
        step.fail("First failure")
        
        # First retry should succeed
        self.assertTrue(step.retry())
        self.assertEqual(step.status, DAGStepStatus.RETRY)
        self.assertEqual(step.retry_count, 1)
        self.assertIsNone(step.error)
        
        # Second retry should succeed
        step.fail("Second failure")
        self.assertTrue(step.retry())
        self.assertEqual(step.retry_count, 2)
        
        # Third retry should fail (exceeds max_retries)
        step.fail("Third failure")
        self.assertFalse(step.retry())
        self.assertEqual(step.retry_count, 2)
        self.assertEqual(step.status, DAGStepStatus.FAILED)
    
    def test_step_skip(self):
        """Test skipping a step."""
        step = DAGStepState(step_id="test_step")
        step.skip("Dependency failed")
        
        self.assertEqual(step.status, DAGStepStatus.SKIPPED)
        self.assertIsNotNone(step.end_time)
        self.assertEqual(step.metadata['skip_reason'], "Dependency failed")
    
    def test_step_cancel(self):
        """Test cancelling a step."""
        step = DAGStepState(step_id="test_step")
        step.start()
        step.cancel()
        
        self.assertEqual(step.status, DAGStepStatus.CANCELLED)
        self.assertIsNotNone(step.end_time)
    
    def test_step_serialization(self):
        """Test step serialization and deserialization."""
        step = DAGStepState(step_id="test_step")
        step.start()
        step.complete({"result": "data"})
        
        # Serialize
        data = step.to_dict()
        self.assertTrue(validate_dag_step_state(data))
        
        # Deserialize
        restored = DAGStepState.from_dict(data)
        self.assertEqual(restored.step_id, step.step_id)
        self.assertEqual(restored.status, step.status)
        self.assertEqual(restored.result, step.result)


class TestDAGRun(unittest.TestCase):
    """Test cases for DAGRun."""
    
    def test_dag_run_creation(self):
        """Test creating a new DAG run."""
        run = DAGRun(dag_id="test_dag")
        self.assertEqual(run.dag_id, "test_dag")
        self.assertIsNotNone(run.run_id)
        self.assertEqual(run.status, DAGRunStatus.CREATED)
        self.assertEqual(len(run.steps), 0)
    
    def test_add_steps(self):
        """Test adding steps to a DAG run."""
        run = DAGRun(dag_id="test_dag")
        
        step1 = run.add_step("step1")
        self.assertIsInstance(step1, DAGStepState)
        self.assertEqual(step1.step_id, "step1")
        self.assertIn("step1", run.steps)
        
        step2 = run.add_step("step2", max_retries=5)
        self.assertEqual(step2.max_retries, 5)
    
    def test_dag_run_lifecycle(self):
        """Test complete DAG run lifecycle."""
        run = DAGRun(dag_id="test_dag")
        
        # Add steps
        step1 = run.add_step("step1")
        step2 = run.add_step("step2")
        step3 = run.add_step("step3")
        
        # Start run
        run.start()
        self.assertEqual(run.status, DAGRunStatus.RUNNING)
        self.assertIsNotNone(run.start_time)
        
        # Execute steps
        step1.start()
        step1.complete({"output": "step1_result"})
        
        step2.start()
        step2.fail("Step 2 failed")
        
        step3.skip("Previous step failed")
        
        # Complete run
        run.complete()
        self.assertEqual(run.status, DAGRunStatus.PARTIAL_SUCCESS)
        self.assertIsNotNone(run.end_time)
        self.assertIsNotNone(run.error)
    
    def test_dag_run_cancel(self):
        """Test cancelling a DAG run."""
        run = DAGRun(dag_id="test_dag")
        
        step1 = run.add_step("step1")
        step2 = run.add_step("step2")
        
        run.start()
        step1.start()
        step1.complete()
        
        # Cancel run
        run.cancel()
        self.assertEqual(run.status, DAGRunStatus.CANCELLED)
        self.assertEqual(step2.status, DAGStepStatus.CANCELLED)
    
    def test_execution_summary(self):
        """Test getting execution summary."""
        run = DAGRun(dag_id="test_dag")
        
        # Setup steps
        step1 = run.add_step("step1")
        step2 = run.add_step("step2")
        step3 = run.add_step("step3")
        
        step1.status = DAGStepStatus.SUCCESS
        step2.status = DAGStepStatus.FAILED
        step3.status = DAGStepStatus.SKIPPED
        
        summary = run.get_execution_summary()
        self.assertEqual(summary['total_steps'], 3)
        self.assertEqual(summary['completed_steps'], 1)
        self.assertEqual(summary['failed_steps'], 1)
        self.assertEqual(summary['skipped_steps'], 1)
        self.assertAlmostEqual(summary['success_rate'], 33.33, places=1)
    
    def test_dag_run_serialization(self):
        """Test DAG run serialization and deserialization."""
        run = DAGRun(dag_id="test_dag")
        run.add_step("step1")
        run.add_step("step2")
        run.start()
        
        # Serialize
        data = run.to_dict()
        self.assertTrue(validate_dag_run(data))
        
        # Deserialize
        restored = DAGRun.from_dict(data)
        self.assertEqual(restored.dag_id, run.dag_id)
        self.assertEqual(restored.run_id, run.run_id)
        self.assertEqual(restored.status, run.status)
        self.assertEqual(len(restored.steps), len(run.steps))


class TestDAGRunStore(unittest.TestCase):
    """Test cases for DAGRunStore."""
    
    def setUp(self):
        """Set up test storage directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = DAGRunStore(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test storage directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_and_get(self):
        """Test creating and retrieving a DAG run."""
        run = DAGRun(dag_id="test_dag")
        run.add_step("step1")
        
        # Create
        run_id = self.store.create(run)
        self.assertEqual(run_id, run.run_id)
        
        # Get
        retrieved = self.store.get(run_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.dag_id, run.dag_id)
        self.assertEqual(len(retrieved.steps), 1)
    
    def test_update(self):
        """Test updating a DAG run."""
        run = DAGRun(dag_id="test_dag")
        self.store.create(run)
        
        # Update
        run.start()
        run.add_step("step1")
        self.store.update(run)
        
        # Verify
        retrieved = self.store.get(run.run_id)
        self.assertEqual(retrieved.status, DAGRunStatus.RUNNING)
        self.assertEqual(len(retrieved.steps), 1)
    
    def test_delete(self):
        """Test deleting a DAG run."""
        run = DAGRun(dag_id="test_dag")
        self.store.create(run)
        
        # Delete
        self.assertTrue(self.store.delete(run.run_id))
        
        # Verify
        self.assertIsNone(self.store.get(run.run_id))
        self.assertFalse(self.store.delete(run.run_id))
    
    def test_list_runs(self):
        """Test listing DAG runs with filters."""
        # Create multiple runs
        run1 = DAGRun(dag_id="dag1")
        run1.status = DAGRunStatus.SUCCESS
        self.store.create(run1)
        
        run2 = DAGRun(dag_id="dag1")
        run2.status = DAGRunStatus.FAILED
        self.store.create(run2)
        
        run3 = DAGRun(dag_id="dag2")
        run3.status = DAGRunStatus.SUCCESS
        self.store.create(run3)
        
        # List all
        all_runs = self.store.list_runs()
        self.assertEqual(len(all_runs), 3)
        
        # Filter by DAG ID
        dag1_runs = self.store.list_runs(dag_id="dag1")
        self.assertEqual(len(dag1_runs), 2)
        
        # Filter by status
        success_runs = self.store.list_runs(status=DAGRunStatus.SUCCESS)
        self.assertEqual(len(success_runs), 2)
    
    def test_get_active_runs(self):
        """Test getting active runs."""
        run1 = DAGRun(dag_id="dag1")
        run1.start()
        self.store.create(run1)
        
        run2 = DAGRun(dag_id="dag2")
        run2.status = DAGRunStatus.SUCCESS
        self.store.create(run2)
        
        active_runs = self.store.get_active_runs()
        self.assertEqual(len(active_runs), 1)
        self.assertEqual(active_runs[0].dag_id, "dag1")
    
    def test_get_statistics(self):
        """Test getting execution statistics."""
        # Create runs with different statuses
        for status in [DAGRunStatus.SUCCESS, DAGRunStatus.SUCCESS, DAGRunStatus.FAILED]:
            run = DAGRun(dag_id="test_dag")
            run.status = status
            self.store.create(run)
        
        stats = self.store.get_statistics()
        self.assertEqual(stats['total_runs'], 3)
        self.assertEqual(stats['by_status']['success'], 2)
        self.assertEqual(stats['by_status']['failed'], 1)
        self.assertAlmostEqual(stats['success_rate'], 66.67, places=1)


if __name__ == '__main__':
    unittest.main()