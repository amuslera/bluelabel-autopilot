"""
Unit tests for DAGRunTraceCollector and trace persistence.
"""

import unittest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import asyncio

from services.workflow.dag_run_trace import DAGRunTraceCollector
from services.workflow.dag_run_store import DAGRunStore
from services.workflow.dag_run_tracker import DAGRun, DAGRunStatus, DAGStepState, DAGStepStatus
from shared.schemas.dag_trace_schema import TraceEventType, DAGRunTrace, StepTraceEntry


class TestDAGRunTrace(unittest.TestCase):
    """Test cases for DAG execution tracing."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = DAGRunStore(storage_path=self.temp_dir)
        self.collector = DAGRunTraceCollector(store=self.store)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_trace_step_lifecycle(self):
        """Test tracing step lifecycle events."""
        # Create DAGRun and trace
        dag_run = DAGRun(
            run_id="test_run_123",
            dag_id="test_dag",
            status=DAGRunStatus.RUNNING
        )
        trace = self.collector.start_dag_trace(dag_run)
        
        # Create step state
        step = DAGStepState(
            step_id="step1",
            status=DAGStepStatus.RUNNING
        )
        
        # Trace step started
        self.collector.trace_step_start(
            dag_run.run_id, 
            step,
            agent_name="TestAgent",
            task_type="process"
        )
        
        # Verify entry was added (including DAG start entry)
        self.assertEqual(len(trace.trace_entries), 2)
        entry = trace.trace_entries[1]  # First is DAG start
        self.assertEqual(entry.step_id, "step1")
        self.assertEqual(entry.event_type, TraceEventType.STEP_START)
        self.assertEqual(entry.agent_name, "TestAgent")
        self.assertEqual(entry.task_type, "process")
        
        # Trace step completed
        step.status = DAGStepStatus.SUCCESS
        self.collector.trace_step_complete(dag_run.run_id, step)
        
        # Verify completion entry
        self.assertEqual(len(trace.trace_entries), 3)
        completion = trace.trace_entries[2]
        self.assertEqual(completion.step_id, "step1")
        self.assertEqual(completion.event_type, TraceEventType.STEP_COMPLETE)
    
    def test_trace_step_retry(self):
        """Test tracing step retries."""
        # Create DAGRun and trace
        dag_run = DAGRun(
            run_id="test_run_456",
            dag_id="test_dag",
            status=DAGRunStatus.RUNNING
        )
        trace = self.collector.start_dag_trace(dag_run)
        
        # Create step state
        step = DAGStepState(
            step_id="step1",
            status=DAGStepStatus.RUNNING,
            retry_count=0,
            max_retries=3
        )
        
        # First attempt fails
        self.collector.trace_step_start(dag_run.run_id, step)
        step.status = DAGStepStatus.FAILED
        step.error = "Connection timeout"
        self.collector.trace_step_fail(dag_run.run_id, step)
        
        # Retry
        step.retry_count = 1
        self.collector.trace_step_retry(dag_run.run_id, step, retry_delay=2.0)
        
        # Verify retry entry
        retry_entry = trace.trace_entries[3]  # DAG start, step start, step fail, retry
        self.assertEqual(retry_entry.event_type, TraceEventType.STEP_RETRY)
        self.assertEqual(retry_entry.retry_attempt, 1)
        
        # Second attempt succeeds
        step.status = DAGStepStatus.RUNNING
        self.collector.trace_step_start(dag_run.run_id, step)
        step.status = DAGStepStatus.SUCCESS
        self.collector.trace_step_complete(dag_run.run_id, step)
        
        # Verify total entries
        self.assertEqual(len(trace.trace_entries), 6)
    
    def test_trace_persistence(self):
        """Test saving and loading traces."""
        # Create DAGRun
        dag_run = DAGRun(
            run_id="test_run_789",
            dag_id="test_dag",
            status=DAGRunStatus.RUNNING
        )
        self.store.create(dag_run)
        
        # Create and populate trace
        trace = self.collector.start_dag_trace(dag_run)
        
        # Add step events
        step1 = DAGStepState(step_id="step1", status=DAGStepStatus.RUNNING)
        self.collector.trace_step_start(dag_run.run_id, step1, agent_name="Agent1")
        step1.status = DAGStepStatus.SUCCESS
        self.collector.trace_step_complete(dag_run.run_id, step1)
        
        step2 = DAGStepState(step_id="step2", status=DAGStepStatus.RUNNING)
        self.collector.trace_step_start(dag_run.run_id, step2, agent_name="Agent2")
        step2.status = DAGStepStatus.FAILED
        step2.error = "Processing error"
        self.collector.trace_step_fail(dag_run.run_id, step2)
        
        # Save trace
        self.store.save_trace(dag_run.run_id, trace)
        
        # Load trace
        loaded_trace = self.store.get_trace(dag_run.run_id)
        
        # Verify loaded trace
        self.assertIsNotNone(loaded_trace)
        self.assertEqual(loaded_trace.run_id, trace.run_id)
        self.assertEqual(loaded_trace.dag_id, trace.dag_id)
        self.assertEqual(len(loaded_trace.trace_entries), 5)  # DAG start + 4 step events
        
        # Verify entries preserved correctly
        self.assertEqual(loaded_trace.trace_entries[1].step_id, "step1")
        self.assertEqual(loaded_trace.trace_entries[1].event_type, TraceEventType.STEP_START)
        self.assertEqual(loaded_trace.trace_entries[1].agent_name, "Agent1")
        
        self.assertEqual(loaded_trace.trace_entries[4].step_id, "step2")
        self.assertEqual(loaded_trace.trace_entries[4].event_type, TraceEventType.STEP_FAIL)
    
    def test_trace_deletion(self):
        """Test trace deletion."""
        # Create DAGRun and trace
        dag_run = DAGRun(
            run_id="test_run_999",
            dag_id="test_dag",
            status=DAGRunStatus.SUCCESS
        )
        self.store.create(dag_run)
        
        trace = self.collector.start_dag_trace(dag_run)
        
        # Add step events
        step = DAGStepState(step_id="step1", status=DAGStepStatus.RUNNING)
        self.collector.trace_step_start(dag_run.run_id, step)
        step.status = DAGStepStatus.SUCCESS
        self.collector.trace_step_complete(dag_run.run_id, step)
        
        # Save trace
        self.store.save_trace(dag_run.run_id, trace)
        
        # Verify trace exists
        self.assertIsNotNone(self.store.get_trace(dag_run.run_id))
        
        # Delete DAGRun (should also delete trace)
        self.assertTrue(self.store.delete(dag_run.run_id))
        
        # Verify trace was deleted
        self.assertIsNone(self.store.get_trace(dag_run.run_id))
    
    def test_trace_run_summary(self):
        """Test complete_dag_trace with run summary."""
        # Create DAGRun
        dag_run = DAGRun(
            run_id="test_run_111",
            dag_id="test_dag",
            status=DAGRunStatus.RUNNING
        )
        dag_run.start_time = datetime.utcnow()
        
        trace = self.collector.start_dag_trace(dag_run)
        
        # Add some step events
        step1 = dag_run.add_step("step1")
        step1.status = DAGStepStatus.SUCCESS
        self.collector.trace_step_start(dag_run.run_id, step1)
        self.collector.trace_step_complete(dag_run.run_id, step1)
        
        step2 = dag_run.add_step("step2")
        step2.status = DAGStepStatus.SUCCESS
        self.collector.trace_step_start(dag_run.run_id, step2)
        self.collector.trace_step_complete(dag_run.run_id, step2)
        
        # Complete DAG
        dag_run.status = DAGRunStatus.SUCCESS
        dag_run.end_time = datetime.utcnow()
        completed_trace = self.collector.complete_dag_trace(dag_run)
        
        # Verify trace was finalized
        self.assertIsNotNone(completed_trace)
        self.assertIsNotNone(completed_trace.end_time)
        self.assertEqual(completed_trace.status, "success")
        self.assertIn('execution_summary', completed_trace.summary)
    
    def test_trace_with_skip_and_info(self):
        """Test tracing skipped steps and info entries."""
        # Create DAGRun
        dag_run = DAGRun(
            run_id="test_run_222",
            dag_id="test_dag",
            status=DAGRunStatus.RUNNING
        )
        trace = self.collector.start_dag_trace(dag_run)
        
        # Add info entry
        self.collector.add_info_entry(
            dag_run.run_id,
            "Starting workflow processing",
            metadata={"source": "email_trigger"}
        )
        
        # Skip a step
        step = DAGStepState(step_id="optional_step", status=DAGStepStatus.SKIPPED)
        self.collector.trace_step_skip(dag_run.run_id, step, reason="Condition not met")
        
        # Verify entries
        self.assertEqual(len(trace.trace_entries), 3)  # DAG start, info, skip
        
        info_entry = trace.trace_entries[1]
        self.assertEqual(info_entry.event_type, TraceEventType.INFO)
        self.assertEqual(info_entry.metadata['message'], "Starting workflow processing")
        
        skip_entry = trace.trace_entries[2]
        self.assertEqual(skip_entry.event_type, TraceEventType.STEP_SKIP)
        self.assertEqual(skip_entry.metadata['skip_reason'], "Condition not met")


if __name__ == "__main__":
    unittest.main()