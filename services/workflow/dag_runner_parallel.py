"""
Parallel DAG Runner with dependency-aware execution.

This module extends the StatefulDAGRunner to support parallel execution
of independent steps while respecting step dependencies.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime

from .dag_runner import StatefulDAGRunner, RetryBackoffStrategy
from .dag_run_tracker import DAGStepStatus, DAGRunStatus
from .dag_run_store import DAGRunStore

logger = logging.getLogger(__name__)


class ParallelStatefulDAGRunner(StatefulDAGRunner):
    """DAG Runner with parallel execution support for independent steps."""

    def __init__(self, 
                 dag_id: str,
                 store: Optional[DAGRunStore] = None,
                 run_id: Optional[str] = None,
                 max_concurrent_steps: int = 5):
        """
        Initialize the parallel DAG runner.
        
        Args:
            dag_id: Identifier of the DAG to execute
            store: DAGRunStore instance (creates default if None)
            run_id: Optional existing run ID to resume
            max_concurrent_steps: Maximum number of steps to run concurrently
        """
        super().__init__(dag_id, store, run_id)
        self.max_concurrent_steps = max_concurrent_steps
        self._step_dependencies: Dict[str, Set[str]] = {}
        self._running_steps: Set[str] = set()
        self._step_lock = asyncio.Lock()
        
    def register_step(self, 
                      step_id: str, 
                      executor: Callable,
                      dependencies: Optional[List[str]] = None,
                      max_retries: int = 3,
                      retry_delay: float = 1.0,
                      retry_backoff: RetryBackoffStrategy = RetryBackoffStrategy.EXPONENTIAL,
                      critical: bool = True):
        """
        Register a step executor function with dependencies.
        
        Args:
            step_id: Unique identifier for the step
            executor: Async callable that executes the step
            dependencies: List of step IDs that must complete before this step
            max_retries: Maximum retry attempts for this step
            retry_delay: Base delay between retries in seconds
            retry_backoff: Backoff strategy for retry delays
            critical: Whether step failure should fail the entire DAG
        """
        # Register with parent class
        super().register_step(
            step_id, executor, max_retries, retry_delay, retry_backoff, critical
        )
        
        # Store dependencies
        self._step_dependencies[step_id] = set(dependencies or [])
        
        # Update step metadata with dependencies
        if dependencies:
            self.dag_run.steps[step_id].metadata['dependencies'] = dependencies
            self._persist_state()
    
    def _get_ready_steps(self) -> List[str]:
        """
        Get list of steps that are ready to run (dependencies satisfied).
        
        Returns:
            List of step IDs ready for execution
        """
        ready_steps = []
        
        for step_id, step in self.dag_run.steps.items():
            # Skip if not pending
            if step.status != DAGStepStatus.PENDING:
                continue
                
            # Skip if already running
            if step_id in self._running_steps:
                continue
            
            # Check dependencies
            dependencies = self._step_dependencies.get(step_id, set())
            dependencies_satisfied = True
            
            for dep_id in dependencies:
                dep_step = self.dag_run.get_step(dep_id)
                if not dep_step:
                    logger.warning(f"Dependency {dep_id} not found for step {step_id}")
                    dependencies_satisfied = False
                    break
                    
                # Dependency must be successful
                if dep_step.status != DAGStepStatus.SUCCESS:
                    # If dependency failed or was skipped, skip this step too
                    if dep_step.status in [DAGStepStatus.FAILED, DAGStepStatus.SKIPPED]:
                        step.skip(f"Dependency {dep_id} {dep_step.status.value}")
                        self._persist_state()
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                ready_steps.append(step_id)
        
        return ready_steps
    
    async def execute(self, step_order: Optional[List[str]] = None) -> 'DAGRun':
        """
        Execute the DAG with parallel execution of independent steps.
        
        Args:
            step_order: Optional list of all step IDs (for validation)
                       Actual execution order determined by dependencies
        
        Returns:
            Updated DAGRun instance
        """
        # Validate all steps are registered
        if step_order:
            for step_id in step_order:
                if step_id not in self._step_executors:
                    raise ValueError(f"Step {step_id} not registered")
        
        # Start DAG if not already running
        if self.dag_run.status == DAGRunStatus.CREATED:
            self.dag_run.start()
            self._persist_state()
            logger.info(f"Started DAGRun {self.run_id}")
        
        # Execute steps in parallel based on dependencies
        try:
            while True:
                # Get ready steps
                async with self._step_lock:
                    ready_steps = self._get_ready_steps()
                    
                    # Limit concurrent executions
                    available_slots = self.max_concurrent_steps - len(self._running_steps)
                    steps_to_run = ready_steps[:available_slots]
                    
                    # Mark steps as running
                    for step_id in steps_to_run:
                        self._running_steps.add(step_id)
                
                # If no steps to run, check if we're done
                if not steps_to_run:
                    # Check if all steps are complete
                    pending_steps = [
                        s for s in self.dag_run.steps.values() 
                        if s.status in [DAGStepStatus.PENDING, DAGStepStatus.RUNNING]
                    ]
                    
                    if not pending_steps:
                        # All steps complete
                        break
                    
                    # If we have running steps, wait a bit
                    if self._running_steps:
                        await asyncio.sleep(0.1)
                        continue
                    
                    # No running steps and pending steps exist - might be deadlock
                    logger.warning(f"Potential dependency deadlock detected. Pending steps: {[s.step_id for s in pending_steps]}")
                    break
                
                # Execute ready steps in parallel
                if steps_to_run:
                    logger.info(f"Executing {len(steps_to_run)} steps in parallel: {steps_to_run}")
                    
                    # Create tasks for parallel execution
                    tasks = []
                    for step_id in steps_to_run:
                        task = asyncio.create_task(self._execute_step_wrapper(step_id))
                        tasks.append(task)
                    
                    # Wait for at least one task to complete
                    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                    
                    # Let remaining tasks continue in background
                    for task in pending:
                        # Don't cancel, let them complete
                        pass
                
                # Check if we should continue
                if self.dag_run.status in [DAGRunStatus.CANCELLED, DAGRunStatus.FAILED]:
                    logger.warning(f"DAGRun {self.run_id} stopped early with status {self.dag_run.status}")
                    
                    # Wait for running steps to complete
                    while self._running_steps:
                        await asyncio.sleep(0.1)
                    
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
        
        return self.dag_run
    
    async def _execute_step_wrapper(self, step_id: str):
        """Wrapper to execute step and update running set."""
        try:
            await self._execute_step(step_id)
        finally:
            async with self._step_lock:
                self._running_steps.discard(step_id)
    
    def _skip_dependent_steps(self, failed_step_id: str):
        """Skip all steps that depend on a failed step."""
        # Find all steps that depend on the failed step
        for step_id, dependencies in self._step_dependencies.items():
            if failed_step_id in dependencies:
                step = self.dag_run.get_step(step_id)
                if step and step.status == DAGStepStatus.PENDING:
                    step.skip(f"Dependency {failed_step_id} failed")
                    # Recursively skip dependents
                    self._skip_dependent_steps(step_id)
        
        self._persist_state()
    
    def _skip_remaining_steps(self, failed_step_id: str):
        """Override to use dependency-aware skipping."""
        if self.dag_run.steps[failed_step_id].metadata.get('critical', True):
            # For critical failures, skip all remaining steps
            super()._skip_remaining_steps(failed_step_id)
        else:
            # For non-critical failures, only skip dependent steps
            self._skip_dependent_steps(failed_step_id)
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the dependency graph for visualization.
        
        Returns:
            Dictionary mapping step IDs to their dependencies
        """
        return {
            step_id: list(deps)
            for step_id, deps in self._step_dependencies.items()
        }
    
    def validate_dependencies(self) -> List[str]:
        """
        Validate the dependency graph for cycles and missing steps.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for missing dependencies
        all_steps = set(self._step_executors.keys())
        for step_id, deps in self._step_dependencies.items():
            for dep in deps:
                if dep not in all_steps:
                    errors.append(f"Step {step_id} depends on non-existent step {dep}")
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            for dep in self._step_dependencies.get(step_id, []):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(step_id)
            return False
        
        for step_id in all_steps:
            if step_id not in visited:
                if has_cycle(step_id):
                    errors.append(f"Circular dependency detected involving step {step_id}")
        
        return errors


class ParallelDAGRunnerFactory:
    """Factory for creating parallel DAG runners."""
    
    @staticmethod
    def create_runner(dag_id: str,
                      store: Optional[DAGRunStore] = None,
                      run_id: Optional[str] = None,
                      max_concurrent_steps: int = 5) -> ParallelStatefulDAGRunner:
        """
        Create a new parallel DAG runner instance.
        
        Args:
            dag_id: DAG identifier
            store: Optional DAGRunStore instance
            run_id: Optional run ID to resume
            max_concurrent_steps: Maximum concurrent executions
        
        Returns:
            ParallelStatefulDAGRunner instance
        """
        return ParallelStatefulDAGRunner(dag_id, store, run_id, max_concurrent_steps)
    
    @staticmethod
    def resume_runner(run_id: str, 
                      store: Optional[DAGRunStore] = None,
                      max_concurrent_steps: int = 5) -> ParallelStatefulDAGRunner:
        """
        Resume an existing DAG run with parallel execution.
        
        Args:
            run_id: Run ID to resume
            store: Optional DAGRunStore instance
            max_concurrent_steps: Maximum concurrent executions
        
        Returns:
            ParallelStatefulDAGRunner instance
        """
        store = store or DAGRunStore()
        dag_run = store.get(run_id)
        if not dag_run:
            raise ValueError(f"DAGRun {run_id} not found")
        
        runner = ParallelStatefulDAGRunner(dag_run.dag_id, store, run_id, max_concurrent_steps)
        
        # Restore dependencies from metadata if available
        for step_id, step in dag_run.steps.items():
            if 'dependencies' in step.metadata:
                runner._step_dependencies[step_id] = set(step.metadata['dependencies'])
        
        return runner