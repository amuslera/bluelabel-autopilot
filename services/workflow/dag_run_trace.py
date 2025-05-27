"""
DAGRun trace collector for structured execution logging.

This module provides utilities for collecting and managing execution
traces for DAG runs, capturing detailed step-level information.
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
import asyncio

from shared.schemas.dag_trace_schema import (
    DAGRunTrace, 
    StepTraceEntry, 
    TraceEventType
)
from .dag_run_tracker import DAGRun, DAGStepState, DAGRunStatus, DAGStepStatus
from .dag_run_store import DAGRunStore

logger = logging.getLogger(__name__)


class DAGRunTraceCollector:
    """Collects execution traces for DAG runs."""
    
    def __init__(self, store: Optional[DAGRunStore] = None):
        """
        Initialize the trace collector.
        
        Args:
            store: DAGRunStore instance for persistence
        """
        self.store = store or DAGRunStore()
        self._active_traces: Dict[str, DAGRunTrace] = {}
        self._step_start_times: Dict[str, datetime] = {}
    
    def start_dag_trace(self, dag_run: DAGRun) -> DAGRunTrace:
        """
        Start tracing a DAG run.
        
        Args:
            dag_run: The DAGRun to trace
            
        Returns:
            DAGRunTrace instance
        """
        trace = DAGRunTrace(
            run_id=dag_run.run_id,
            dag_id=dag_run.dag_id,
            start_time=dag_run.start_time or datetime.utcnow(),
            status=dag_run.status.value
        )
        
        # Add DAG start event
        entry = StepTraceEntry(
            step_id="__dag__",
            event_type=TraceEventType.DAG_START,
            timestamp=trace.start_time,
            metadata={
                'dag_metadata': dag_run.metadata
            }
        )
        trace.add_entry(entry)
        
        self._active_traces[dag_run.run_id] = trace
        logger.info(f"Started tracing DAGRun {dag_run.run_id}")
        
        return trace
    
    def trace_step_start(self, 
                        run_id: str, 
                        step: DAGStepState,
                        agent_name: Optional[str] = None,
                        task_type: Optional[str] = None,
                        input_summary: Optional[Dict[str, Any]] = None) -> None:
        """
        Trace the start of a step execution.
        
        Args:
            run_id: DAG run ID
            step: Step state
            agent_name: Name of the agent executing the step
            task_type: Type of task being executed
            input_summary: Summary of step input
        """
        trace = self._get_trace(run_id)
        if not trace:
            return
        
        timestamp = step.start_time or datetime.utcnow()
        self._step_start_times[f"{run_id}:{step.step_id}"] = timestamp
        
        entry = StepTraceEntry(
            step_id=step.step_id,
            event_type=TraceEventType.STEP_START,
            timestamp=timestamp,
            retry_attempt=step.retry_count,
            agent_name=agent_name,
            task_type=task_type,
            input_summary=input_summary,
            metadata=step.metadata
        )
        
        trace.add_entry(entry)
        logger.debug(f"Traced step start: {step.step_id} in run {run_id}")
    
    def trace_step_complete(self,
                           run_id: str,
                           step: DAGStepState,
                           output_summary: Optional[Dict[str, Any]] = None) -> None:
        """
        Trace the completion of a step.
        
        Args:
            run_id: DAG run ID
            step: Step state
            output_summary: Summary of step output
        """
        trace = self._get_trace(run_id)
        if not trace:
            return
        
        timestamp = step.end_time or datetime.utcnow()
        duration_ms = self._calculate_duration(run_id, step.step_id, timestamp)
        
        entry = StepTraceEntry(
            step_id=step.step_id,
            event_type=TraceEventType.STEP_COMPLETE,
            timestamp=timestamp,
            duration_ms=duration_ms,
            retry_attempt=step.retry_count,
            output_summary=output_summary or step.result,
            metadata=step.metadata
        )
        
        trace.add_entry(entry)
        logger.debug(f"Traced step complete: {step.step_id} in run {run_id}")
    
    def trace_step_fail(self,
                       run_id: str,
                       step: DAGStepState,
                       error_details: Optional[Dict[str, Any]] = None) -> None:
        """
        Trace a step failure.
        
        Args:
            run_id: DAG run ID
            step: Step state
            error_details: Detailed error information
        """
        trace = self._get_trace(run_id)
        if not trace:
            return
        
        timestamp = step.end_time or datetime.utcnow()
        duration_ms = self._calculate_duration(run_id, step.step_id, timestamp)
        
        error_info = error_details or {}
        if step.error and 'error' not in error_info:
            error_info['error'] = step.error
        
        # Include error history from metadata if available
        if 'error_history' in step.metadata:
            error_info['error_history'] = step.metadata['error_history']
        
        entry = StepTraceEntry(
            step_id=step.step_id,
            event_type=TraceEventType.STEP_FAIL,
            timestamp=timestamp,
            duration_ms=duration_ms,
            retry_attempt=step.retry_count,
            error_details=error_info,
            metadata=step.metadata
        )
        
        trace.add_entry(entry)
        logger.debug(f"Traced step fail: {step.step_id} in run {run_id}")
    
    def trace_step_retry(self,
                        run_id: str,
                        step: DAGStepState,
                        retry_delay: float) -> None:
        """
        Trace a step retry attempt.
        
        Args:
            run_id: DAG run ID
            step: Step state
            retry_delay: Delay before retry in seconds
        """
        trace = self._get_trace(run_id)
        if not trace:
            return
        
        entry = StepTraceEntry(
            step_id=step.step_id,
            event_type=TraceEventType.STEP_RETRY,
            timestamp=datetime.utcnow(),
            retry_attempt=step.retry_count,
            metadata={
                'retry_delay_seconds': retry_delay,
                'max_retries': step.max_retries,
                'retry_backoff': step.metadata.get('retry_backoff', 'exponential')
            }
        )
        
        trace.add_entry(entry)
        logger.debug(f"Traced step retry: {step.step_id} (attempt {step.retry_count}) in run {run_id}")
    
    def trace_step_skip(self,
                       run_id: str,
                       step: DAGStepState,
                       reason: str) -> None:
        """
        Trace a skipped step.
        
        Args:
            run_id: DAG run ID
            step: Step state
            reason: Reason for skipping
        """
        trace = self._get_trace(run_id)
        if not trace:
            return
        
        entry = StepTraceEntry(
            step_id=step.step_id,
            event_type=TraceEventType.STEP_SKIP,
            timestamp=datetime.utcnow(),
            metadata={
                'skip_reason': reason
            }
        )
        
        trace.add_entry(entry)
        logger.debug(f"Traced step skip: {step.step_id} in run {run_id}")
    
    def complete_dag_trace(self, dag_run: DAGRun) -> Optional[DAGRunTrace]:
        """
        Complete tracing for a DAG run.
        
        Args:
            dag_run: The completed DAGRun
            
        Returns:
            Completed DAGRunTrace or None
        """
        trace = self._get_trace(dag_run.run_id)
        if not trace:
            return None
        
        trace.end_time = dag_run.end_time or datetime.utcnow()
        trace.status = dag_run.status.value
        
        # Add DAG completion event
        event_type = (TraceEventType.DAG_COMPLETE 
                     if dag_run.status == DAGRunStatus.SUCCESS 
                     else TraceEventType.DAG_FAIL)
        
        entry = StepTraceEntry(
            step_id="__dag__",
            event_type=event_type,
            timestamp=trace.end_time,
            duration_ms=int((trace.end_time - trace.start_time).total_seconds() * 1000),
            metadata={
                'final_status': dag_run.status.value,
                'error': dag_run.error,
                'total_retries': dag_run.total_retries
            }
        )
        trace.add_entry(entry)
        
        # Generate summary
        trace.summary = {
            'execution_summary': dag_run.get_execution_summary(),
            'step_count': len(dag_run.steps),
            'total_duration_seconds': dag_run.duration_seconds
        }
        
        # Clean up
        del self._active_traces[dag_run.run_id]
        
        logger.info(f"Completed tracing DAGRun {dag_run.run_id}")
        return trace
    
    def add_info_entry(self,
                      run_id: str,
                      message: str,
                      step_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an informational trace entry.
        
        Args:
            run_id: DAG run ID
            message: Info message
            step_id: Optional step ID
            metadata: Additional metadata
        """
        trace = self._get_trace(run_id)
        if not trace:
            return
        
        entry = StepTraceEntry(
            step_id=step_id or "__dag__",
            event_type=TraceEventType.INFO,
            timestamp=datetime.utcnow(),
            metadata={
                'message': message,
                **(metadata or {})
            }
        )
        
        trace.add_entry(entry)
    
    def get_trace(self, run_id: str) -> Optional[DAGRunTrace]:
        """
        Get the trace for a DAG run.
        
        Args:
            run_id: DAG run ID
            
        Returns:
            DAGRunTrace or None
        """
        return self._active_traces.get(run_id)
    
    def _get_trace(self, run_id: str) -> Optional[DAGRunTrace]:
        """Internal method to get trace with logging."""
        trace = self._active_traces.get(run_id)
        if not trace:
            logger.warning(f"No active trace found for run {run_id}")
        return trace
    
    def _calculate_duration(self, run_id: str, step_id: str, end_time: datetime) -> Optional[int]:
        """Calculate step duration in milliseconds."""
        key = f"{run_id}:{step_id}"
        start_time = self._step_start_times.get(key)
        
        if start_time:
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            # Clean up
            del self._step_start_times[key]
            return duration_ms
        
        return None