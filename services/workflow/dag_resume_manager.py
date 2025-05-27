"""
DAG Resume Manager for handling incomplete runs.

This module provides functionality to detect and resume incomplete DAG runs
from their last valid state, enabling recovery from failures and interruptions.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from .dag_run_tracker import DAGRun, DAGRunStatus, DAGStepStatus, DAGStepState
from .dag_run_store import DAGRunStore
from .dag_run_trace import DAGRunTraceCollector
from shared.schemas.dag_trace_schema import DAGRunTrace, TraceEventType

logger = logging.getLogger(__name__)


class DAGResumeManager:
    """Manages the resumption of incomplete DAG runs."""
    
    def __init__(self, store: Optional[DAGRunStore] = None):
        """
        Initialize the resume manager.
        
        Args:
            store: DAGRunStore instance for persistence
        """
        self.store = store or DAGRunStore()
        self.trace_collector = DAGRunTraceCollector(store=self.store)
    
    def find_incomplete_runs(self, dag_id: Optional[str] = None) -> List[DAGRun]:
        """
        Find all incomplete DAG runs.
        
        Args:
            dag_id: Optional filter by DAG ID
            
        Returns:
            List of incomplete DAGRun instances
        """
        incomplete_runs = []
        
        # Check for running, failed, or partially completed runs
        for status in [DAGRunStatus.RUNNING, DAGRunStatus.FAILED]:
            runs = self.store.list_runs(dag_id=dag_id, status=status)
            for run_info in runs:
                dag_run = self.store.get(run_info['run_id'])
                if dag_run and self._is_resumable(dag_run):
                    incomplete_runs.append(dag_run)
        
        logger.info(f"Found {len(incomplete_runs)} incomplete runs")
        return incomplete_runs
    
    def can_resume(self, run_id: str) -> Tuple[bool, str]:
        """
        Check if a DAG run can be resumed.
        
        Args:
            run_id: The run ID to check
            
        Returns:
            Tuple of (can_resume, reason)
        """
        dag_run = self.store.get(run_id)
        if not dag_run:
            return False, "DAG run not found"
        
        if dag_run.status == DAGRunStatus.SUCCESS:
            return False, "DAG run already completed successfully"
        
        if dag_run.status == DAGRunStatus.CANCELLED:
            return False, "DAG run was cancelled"
        
        # Check if we have trace data (optional for now)
        trace = self.store.get_trace(run_id)
        # if not trace:
        #     return False, "No execution trace found"
        
        # Check for any pending or failed steps
        has_work = any(
            step.status in [DAGStepStatus.PENDING, DAGStepStatus.FAILED]
            for step in dag_run.steps.values()
        )
        
        if not has_work:
            return False, "No pending or failed steps to resume"
        
        return True, "DAG run can be resumed"
    
    def get_resume_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the resume state for a DAG run.
        
        Args:
            run_id: The run ID
            
        Returns:
            Resume state dictionary or None
        """
        dag_run = self.store.get(run_id)
        if not dag_run:
            return None
        
        trace = self.store.get_trace(run_id)
        
        # Analyze current state
        completed_steps = []
        failed_steps = []
        pending_steps = []
        skipped_steps = []
        
        for step_id, step in dag_run.steps.items():
            if step.status == DAGStepStatus.SUCCESS:
                completed_steps.append(step_id)
            elif step.status == DAGStepStatus.FAILED:
                failed_steps.append(step_id)
            elif step.status == DAGStepStatus.PENDING:
                pending_steps.append(step_id)
            elif step.status == DAGStepStatus.SKIPPED:
                skipped_steps.append(step_id)
        
        # Get last successful step from trace
        last_successful_step = None
        if trace:
            success_events = trace.get_events_by_type(TraceEventType.STEP_COMPLETE)
            if success_events:
                last_successful_step = success_events[-1].step_id
        
        resume_state = {
            'run_id': run_id,
            'dag_id': dag_run.dag_id,
            'status': dag_run.status.value,
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'pending_steps': pending_steps,
            'skipped_steps': skipped_steps,
            'last_successful_step': last_successful_step,
            'total_retries': dag_run.total_retries,
            'can_resume': self.can_resume(run_id)[0],
            'resume_from_step': self._determine_resume_point(dag_run, trace)
        }
        
        logger.info(f"Resume state for {run_id}: {len(completed_steps)} completed, "
                   f"{len(failed_steps)} failed, {len(pending_steps)} pending")
        
        return resume_state
    
    def prepare_for_resume(self, run_id: str) -> Optional[DAGRun]:
        """
        Prepare a DAG run for resumption.
        
        Args:
            run_id: The run ID to resume
            
        Returns:
            Prepared DAGRun instance or None
        """
        can_resume, reason = self.can_resume(run_id)
        if not can_resume:
            logger.warning(f"Cannot resume {run_id}: {reason}")
            return None
        
        dag_run = self.store.get(run_id)
        trace = self.store.get_trace(run_id)
        
        # Update run status to RUNNING
        dag_run.status = DAGRunStatus.RUNNING
        dag_run.metadata['resumed_at'] = datetime.utcnow().isoformat()
        dag_run.metadata['resume_count'] = dag_run.metadata.get('resume_count', 0) + 1
        
        # Reset failed and skipped steps to PENDING for retry
        for step_id, step in dag_run.steps.items():
            if step.status == DAGStepStatus.FAILED:
                # Reset status and retry count for fresh start
                step.status = DAGStepStatus.PENDING
                step.retry_count = 0  # Reset retry count
                step.error = None  # Clear error
                logger.info(f"Reset failed step {step_id} to PENDING for retry")
            elif step.status == DAGStepStatus.SKIPPED:
                # Reset skipped steps that were skipped due to failures
                step.status = DAGStepStatus.PENDING
                step.metadata.pop('skip_reason', None)
                logger.info(f"Reset skipped step {step_id} to PENDING for retry")
        
        # Save updated state
        self.store.update(dag_run)
        
        # Add resume event to trace
        if trace:
            self.trace_collector.add_info_entry(
                run_id,
                f"DAG run resumed (attempt #{dag_run.metadata['resume_count']})",
                metadata={
                    'resume_state': self.get_resume_state(run_id),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            self.store.save_trace(run_id, trace)
        
        logger.info(f"Prepared DAG run {run_id} for resume")
        return dag_run
    
    def _is_resumable(self, dag_run: DAGRun) -> bool:
        """Check if a DAG run is resumable."""
        # Cannot resume cancelled or already successful runs
        if dag_run.status in [DAGRunStatus.CANCELLED, DAGRunStatus.SUCCESS]:
            return False
        
        # Must have at least one non-successful step
        has_incomplete = any(
            step.status != DAGStepStatus.SUCCESS
            for step in dag_run.steps.values()
        )
        
        return has_incomplete
    
    def _determine_resume_point(self, dag_run: DAGRun, 
                               trace: Optional[DAGRunTrace]) -> Optional[str]:
        """
        Determine the optimal step to resume from.
        
        Args:
            dag_run: The DAG run
            trace: Optional execution trace
            
        Returns:
            Step ID to resume from or None
        """
        # First, try to find the first failed step
        for step_id, step in dag_run.steps.items():
            if step.status == DAGStepStatus.FAILED:
                return step_id
        
        # If no failed steps, find the first pending step
        for step_id, step in dag_run.steps.items():
            if step.status == DAGStepStatus.PENDING:
                return step_id
        
        # If trace available, check for any interrupted steps
        if trace:
            # Find steps that started but didn't complete
            started_steps = {e.step_id for e in trace.get_events_by_type(TraceEventType.STEP_START)}
            completed_steps = {e.step_id for e in trace.get_events_by_type(TraceEventType.STEP_COMPLETE)}
            interrupted = started_steps - completed_steps
            
            if interrupted:
                # Return the first interrupted step
                return next(iter(interrupted))
        
        return None
    
    def get_resume_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about resumable runs.
        
        Returns:
            Dictionary of resume statistics
        """
        all_runs = self.store.list_runs(limit=1000)
        
        stats = {
            'total_runs': len(all_runs),
            'resumable_runs': 0,
            'failed_runs': 0,
            'running_runs': 0,
            'resume_candidates': []
        }
        
        for run_info in all_runs:
            if run_info['status'] == 'failed':
                stats['failed_runs'] += 1
            elif run_info['status'] == 'running':
                stats['running_runs'] += 1
            
            can_resume, reason = self.can_resume(run_info['run_id'])
            if can_resume:
                stats['resumable_runs'] += 1
                stats['resume_candidates'].append({
                    'run_id': run_info['run_id'],
                    'dag_id': run_info['dag_id'],
                    'status': run_info['status'],
                    'updated_at': run_info.get('updated_at')
                })
        
        return stats