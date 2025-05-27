"""
Stateful DAG Runner using persistent DAGRun state.

This module provides the core DAG execution engine that integrates with
the DAGRun state tracker for persistent, resumable workflow execution.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from datetime import datetime

from .dag_run_tracker import DAGRun, DAGStepStatus, DAGRunStatus
from .dag_run_store import DAGRunStore
from .dag_resume_manager import DAGResumeManager
from .dag_run_trace import DAGRunTraceCollector

logger = logging.getLogger(__name__)


class RetryBackoffStrategy(Enum):
    """Backoff strategies for retry delays."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"


class StatefulDAGRunner:
    """Executes DAGs with persistent state tracking."""

    def __init__(self, 
                 dag_id: str,
                 store: Optional[DAGRunStore] = None,
                 run_id: Optional[str] = None,
                 resume_mode: bool = False):
        """
        Initialize the stateful DAG runner.
        
        Args:
            dag_id: Identifier of the DAG to execute
            store: DAGRunStore instance (creates default if None)
            run_id: Optional existing run ID to resume
            resume_mode: Whether to enable resume mode for incomplete runs
        """
        self.dag_id = dag_id
        self.store = store or DAGRunStore()
        self.resume_mode = resume_mode
        self.resume_manager = DAGResumeManager(store=self.store)
        self.trace_collector = DAGRunTraceCollector(store=self.store)
        
        # Load existing run or create new one
        if run_id:
            # If resume mode, prepare the run for resumption
            if resume_mode:
                self.dag_run = self.resume_manager.prepare_for_resume(run_id)
                if not self.dag_run:
                    raise ValueError(f"Cannot resume DAGRun {run_id}")
                logger.info(f"Prepared DAGRun {run_id} for resume")
            else:
                self.dag_run = self.store.get(run_id)
                if not self.dag_run:
                    raise ValueError(f"DAGRun {run_id} not found")
                if self.dag_run.dag_id != dag_id:
                    raise ValueError(f"DAGRun {run_id} is for DAG {self.dag_run.dag_id}, not {dag_id}")
                logger.info(f"Loading existing DAGRun {run_id} for DAG {dag_id}")
        else:
            self.dag_run = DAGRun(dag_id=dag_id)
            self.store.create(self.dag_run)
            logger.info(f"Created new DAGRun {self.dag_run.run_id} for DAG {dag_id}")
            
        # Initialize trace if new run
        if not run_id or resume_mode:
            self.trace = self.trace_collector.start_dag_trace(self.dag_run)
        else:
            self.trace = self.trace_collector.get_trace(self.dag_run.run_id)

        # Step executors registry
        self._step_executors: Dict[str, Callable] = {}
        
    @property
    def run_id(self) -> str:
        """Get the current run ID."""
        return self.dag_run.run_id

    def register_step(self, 
                      step_id: str, 
                      executor: Callable, 
                      max_retries: int = 3,
                      retry_delay: float = 1.0,
                      retry_backoff: RetryBackoffStrategy = RetryBackoffStrategy.EXPONENTIAL,
                      critical: bool = True):
        """
        Register a step executor function.
        
        Args:
            step_id: Unique identifier for the step
            executor: Async callable that executes the step
            max_retries: Maximum retry attempts for this step (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1.0)
            retry_backoff: Backoff strategy for retry delays (default: EXPONENTIAL)
            critical: Whether step failure should fail the entire DAG (default: True)
        """
        self._step_executors[step_id] = executor
        
        # Add step to DAGRun if not already present
        if step_id not in self.dag_run.steps:
            self.dag_run.add_step(step_id, max_retries=max_retries)
            # Store retry configuration in step metadata
            self.dag_run.steps[step_id].metadata.update({
                'retry_delay': retry_delay,
                'retry_backoff': retry_backoff.value,
                'critical': critical
            })
            self._persist_state()

    def _persist_state(self):
        """Persist current DAGRun state to storage."""
        try:
            self.store.update(self.dag_run)
            logger.debug(f"Persisted state for run {self.run_id}")
        except Exception as e:
            logger.error(f"Failed to persist state: {e}")
            raise
    
    def _calculate_retry_delay(self, retry_count: int, step_metadata: Dict[str, Any]) -> float:
        """
        Calculate retry delay based on backoff strategy.
        
        Args:
            retry_count: Current retry attempt number (1-based)
            step_metadata: Step metadata containing retry configuration
            
        Returns:
            Delay in seconds before next retry
        """
        base_delay = step_metadata.get('retry_delay', 1.0)
        backoff_strategy = step_metadata.get('retry_backoff', 'exponential')
        
        if backoff_strategy == RetryBackoffStrategy.EXPONENTIAL.value:
            # Exponential backoff: base_delay * (2 ^ (retry_count - 1))
            return base_delay * (2 ** (retry_count - 1))
        elif backoff_strategy == RetryBackoffStrategy.LINEAR.value:
            # Linear backoff: base_delay * retry_count
            return base_delay * retry_count
        elif backoff_strategy == RetryBackoffStrategy.CONSTANT.value:
            # Constant backoff: always base_delay
            return base_delay
        else:
            # Default to exponential if unknown strategy
            logger.warning(f"Unknown backoff strategy: {backoff_strategy}, using exponential")
            return base_delay * (2 ** (retry_count - 1))

    async def execute(self, step_order: Optional[List[str]] = None) -> DAGRun:
        """
        Execute the DAG with state tracking.
        
        Args:
            step_order: Optional ordered list of step IDs to execute
                       If None, executes all registered steps in registration order

        Returns:
            Updated DAGRun instance
        """
        # Determine execution order
        if step_order is None:
            step_order = list(self._step_executors.keys())

        # Validate all steps are registered
        for step_id in step_order:
            if step_id not in self._step_executors:
                raise ValueError(f"Step {step_id} not registered")

        # Start DAG if not already running
        if self.dag_run.status == DAGRunStatus.CREATED:
            self.dag_run.start()
            self._persist_state()
            logger.info(f"Started DAGRun {self.run_id}")

        # Execute steps
        try:
            for step_id in step_order:
                await self._execute_step(step_id)

                # Check if we should continue
                if self.dag_run.status in [DAGRunStatus.CANCELLED, DAGRunStatus.FAILED]:
                    logger.warning(f"DAGRun {self.run_id} stopped early with status {self.dag_run.status}")
                    break

            # Complete the DAG run
            if self.dag_run.status == DAGRunStatus.RUNNING:
                self.dag_run.complete()
                self._persist_state()
                logger.info(f"Completed DAGRun {self.run_id} with status {self.dag_run.status}")

        except Exception as e:
            # Mark DAG as failed
            self.dag_run.fail(str(e))
            # Add detailed error to metadata
            if 'errors' not in self.dag_run.metadata:
                self.dag_run.metadata['errors'] = []
            self.dag_run.metadata['errors'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'dag_execution_error',
                'error': str(e),
                'error_type': type(e).__name__
            })
            self._persist_state()
            logger.error(f"DAGRun {self.run_id} failed: {e}")
            raise

        finally:
            # Update retry count
            self.dag_run.update_retry_count()
            self._persist_state()
            
            # Complete trace
            if self.trace:
                completed_trace = self.trace_collector.complete_dag_trace(self.dag_run)
                if completed_trace:
                    self.store.save_trace(self.dag_run.run_id, completed_trace)

        return self.dag_run

    async def _execute_step(self, step_id: str):
        """Execute a single step with state tracking."""
        step = self.dag_run.get_step(step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found in DAGRun")

        # Skip if already completed
        if step.status == DAGStepStatus.SUCCESS:
            logger.info(f"Step {step_id} already completed, skipping")
            if self.resume_mode:
                # Add skip event to trace
                self.trace_collector.add_info_entry(
                    self.dag_run.run_id,
                    f"Skipped completed step during resume",
                    step_id=step_id
                )
            return

        # Skip if cancelled
        if step.status == DAGStepStatus.CANCELLED:
            logger.info(f"Step {step_id} was cancelled, skipping")
            return

        # Skip if dependencies failed (would be set by orchestrator)
        if step.status == DAGStepStatus.SKIPPED:
            logger.info(f"Step {step_id} was skipped, continuing")
            return

        # Get executor
        executor = self._step_executors.get(step_id)
        if not executor:
            raise ValueError(f"No executor registered for step {step_id}")

        # Execute with retries
        retry_count = 0
        max_retries = step.max_retries

        while retry_count <= max_retries:
            try:
                # Start step
                step.start()
                self._persist_state()
                logger.info(f"Executing step {step_id} (attempt {retry_count + 1}/{max_retries + 1})")
                
                # Trace step start
                self.trace_collector.trace_step_start(
                    self.dag_run.run_id,
                    step,
                    agent_name=step.metadata.get('agent_name'),
                    task_type=step.metadata.get('task_type')
                )

                # Execute
                result = await executor()

                # Complete step
                step.complete(result)
                self._persist_state()
                
                # Trace step completion
                self.trace_collector.trace_step_complete(
                    self.dag_run.run_id,
                    step,
                    output_summary={'result': str(result)[:500] if result else None}
                )
                
                logger.info(f"Step {step_id} completed successfully")
                return

            except Exception as e:
                # Fail step
                step.fail(str(e))
                
                # Add detailed error to step metadata
                if 'error_history' not in step.metadata:
                    step.metadata['error_history'] = []
                step.metadata['error_history'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'attempt': retry_count + 1,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                self._persist_state()
                
                # Trace step failure
                self.trace_collector.trace_step_fail(
                    self.dag_run.run_id,
                    step,
                    error_details={
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'attempt': retry_count + 1
                    }
                )
                
                logger.error(f"Step {step_id} failed (attempt {retry_count + 1}): {e}")

                # Check if we should retry
                if retry_count < max_retries:
                    if step.retry():
                        retry_count += 1
                        self._persist_state()
                        logger.info(f"Retrying step {step_id} (attempt {retry_count + 1}/{max_retries + 1})")

                        # Calculate retry delay based on backoff strategy
                        retry_delay = self._calculate_retry_delay(retry_count, step.metadata)
                        
                        # Trace retry event
                        self.trace_collector.trace_step_retry(
                            self.dag_run.run_id,
                            step,
                            retry_delay=retry_delay
                        )
                        
                        logger.debug(f"Waiting {retry_delay}s before retry (backoff: {step.metadata.get('retry_backoff', 'exponential')})")
                        await asyncio.sleep(retry_delay)
                        continue

                # No more retries, step remains failed
                logger.error(f"Step {step_id} failed after {retry_count + 1} attempts")
                
                # Add final failure to DAG metadata
                if 'step_failures' not in self.dag_run.metadata:
                    self.dag_run.metadata['step_failures'] = []
                self.dag_run.metadata['step_failures'].append({
                    'step_id': step_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'attempts': retry_count + 1,
                    'final_error': str(e),
                    'critical': step.metadata.get('critical', True)
                })

                # Check if this is a critical failure
                if step.metadata.get('critical', True):
                    # Mark remaining steps as skipped
                    self._skip_remaining_steps(step_id)
                    self.dag_run.status = DAGRunStatus.FAILED
                    self.dag_run.metadata['failure_reason'] = f"Critical step '{step_id}' failed after {retry_count + 1} attempts: {str(e)}"
                    self._persist_state()
                else:
                    # Non-critical failure - continue execution
                    logger.warning(f"Non-critical step {step_id} failed, continuing DAG execution")
                    # Mark overall run as partial success if not already failed
                    if self.dag_run.status not in [DAGRunStatus.FAILED, DAGRunStatus.CANCELLED]:
                        self.dag_run.status = DAGRunStatus.PARTIAL_SUCCESS

                return

    def _skip_remaining_steps(self, failed_step_id: str):
        """Skip all steps after a critical failure."""
        # This would be more sophisticated with dependency tracking
        # For now, we'll just mark all pending steps as skipped
        for step_id, step in self.dag_run.steps.items():
            if step.status == DAGStepStatus.PENDING:
                step.skip(f"Skipped due to failure of {failed_step_id}")
        logger.info(f"Skipped remaining steps due to failure of {failed_step_id}")

    async def cancel(self):
        """Cancel the DAG run."""
        self.dag_run.cancel()
        self._persist_state()
        logger.info(f"Cancelled DAGRun {self.run_id}")

    def get_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            'run_id': self.run_id,
            'dag_id': self.dag_id,
            'status': self.dag_run.status.value,
            'summary': self.dag_run.get_execution_summary(),
            'steps': {
                step_id: {
                    'status': step.status.value,
                    'retry_count': step.retry_count,
                    'error': step.error,
                    'duration': step.duration_seconds
                }
                for step_id, step in self.dag_run.steps.items()
            }
        }


class DAGRunnerFactory:
    """Factory for creating DAG runners."""

    @staticmethod
    def create_runner(dag_id: str,
                      store: Optional[DAGRunStore] = None,
                      run_id: Optional[str] = None) -> StatefulDAGRunner:
        """
        Create a new DAG runner instance.
        
        Args:
            dag_id: DAG identifier
            store: Optional DAGRunStore instance
            run_id: Optional run ID to resume

        Returns:
            StatefulDAGRunner instance
        """
        return StatefulDAGRunner(dag_id, store, run_id)

    @staticmethod
    def resume_runner(run_id: str, store: Optional[DAGRunStore] = None) -> StatefulDAGRunner:
        """
        Resume an existing DAG run.
        
        Args:
            run_id: Run ID to resume
            store: Optional DAGRunStore instance

        Returns:
            StatefulDAGRunner instance
        """
        store = store or DAGRunStore()
        dag_run = store.get(run_id)
        if not dag_run:
            raise ValueError(f"DAGRun {run_id} not found")

        return StatefulDAGRunner(dag_run.dag_id, store, run_id, resume_mode=True)
