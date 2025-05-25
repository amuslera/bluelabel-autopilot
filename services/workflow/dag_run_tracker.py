"""
DAGRun State Tracker for workflow execution monitoring.

This module provides the core data structures for tracking DAG workflow executions,
including per-step state, retry status, and execution metadata.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class DAGStepStatus(Enum):
    """Status states for individual DAG steps."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class DAGRunStatus(Enum):
    """Overall status states for DAG runs."""
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"
    PARTIAL_SUCCESS = "partial_success"


@dataclass
class DAGStepState:
    """State information for a single DAG step."""
    step_id: str
    status: DAGStepStatus = DAGStepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def start(self) -> None:
        """Mark step as started."""
        self.status = DAGStepStatus.RUNNING
        self.start_time = datetime.utcnow()
    
    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark step as successfully completed."""
        self.status = DAGStepStatus.SUCCESS
        self.end_time = datetime.utcnow()
        self.result = result
    
    def fail(self, error: str) -> None:
        """Mark step as failed."""
        self.status = DAGStepStatus.FAILED
        self.end_time = datetime.utcnow()
        self.error = error
    
    def retry(self) -> bool:
        """Attempt to retry the step."""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = DAGStepStatus.RETRY
            self.error = None
            return True
        return False
    
    def skip(self, reason: str = "Dependency failed") -> None:
        """Mark step as skipped."""
        self.status = DAGStepStatus.SKIPPED
        self.end_time = datetime.utcnow()
        self.metadata['skip_reason'] = reason
    
    def cancel(self) -> None:
        """Mark step as cancelled."""
        self.status = DAGStepStatus.CANCELLED
        self.end_time = datetime.utcnow()
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate step execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'step_id': self.step_id,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error': self.error,
            'result': self.result,
            'metadata': self.metadata,
            'duration_seconds': self.duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DAGStepState':
        """Create from dictionary."""
        step = cls(
            step_id=data['step_id'],
            status=DAGStepStatus(data['status']),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            error=data.get('error'),
            result=data.get('result'),
            metadata=data.get('metadata', {})
        )
        
        if data.get('start_time'):
            step.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            step.end_time = datetime.fromisoformat(data['end_time'])
        
        return step


@dataclass
class DAGRun:
    """Complete state tracking for a DAG workflow execution."""
    dag_id: str
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: DAGRunStatus = DAGRunStatus.CREATED
    steps: Dict[str, DAGStepState] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_retries: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step_id: str, max_retries: int = 3) -> DAGStepState:
        """Add a new step to track."""
        step = DAGStepState(step_id=step_id, max_retries=max_retries)
        self.steps[step_id] = step
        return step
    
    def get_step(self, step_id: str) -> Optional[DAGStepState]:
        """Get step state by ID."""
        return self.steps.get(step_id)
    
    def start(self) -> None:
        """Mark DAG run as started."""
        self.status = DAGRunStatus.RUNNING
        self.start_time = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark DAG run as completed."""
        # Check if all steps succeeded
        failed_steps = [s for s in self.steps.values() 
                       if s.status == DAGStepStatus.FAILED]
        successful_steps = [s for s in self.steps.values() 
                           if s.status == DAGStepStatus.SUCCESS]
        
        if failed_steps:
            if successful_steps:
                self.status = DAGRunStatus.PARTIAL_SUCCESS
            else:
                self.status = DAGRunStatus.FAILED
            self.error = f"{len(failed_steps)} step(s) failed"
        else:
            self.status = DAGRunStatus.SUCCESS
        
        self.end_time = datetime.utcnow()
    
    def fail(self, error: str) -> None:
        """Mark DAG run as failed."""
        self.status = DAGRunStatus.FAILED
        self.end_time = datetime.utcnow()
        self.error = error
    
    def cancel(self) -> None:
        """Cancel the DAG run."""
        self.status = DAGRunStatus.CANCELLED
        self.end_time = datetime.utcnow()
        
        # Cancel all pending steps
        for step in self.steps.values():
            if step.status in [DAGStepStatus.PENDING, DAGStepStatus.RUNNING]:
                step.cancel()
    
    def update_retry_count(self) -> None:
        """Update total retry count from all steps."""
        self.total_retries = sum(step.retry_count for step in self.steps.values())
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_running(self) -> bool:
        """Check if DAG is currently running."""
        return self.status == DAGRunStatus.RUNNING
    
    @property
    def is_complete(self) -> bool:
        """Check if DAG execution is complete."""
        return self.status in [
            DAGRunStatus.SUCCESS,
            DAGRunStatus.FAILED,
            DAGRunStatus.CANCELLED,
            DAGRunStatus.PARTIAL_SUCCESS
        ]
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary statistics."""
        total_steps = len(self.steps)
        completed_steps = sum(1 for s in self.steps.values() 
                            if s.status == DAGStepStatus.SUCCESS)
        failed_steps = sum(1 for s in self.steps.values() 
                          if s.status == DAGStepStatus.FAILED)
        skipped_steps = sum(1 for s in self.steps.values() 
                           if s.status == DAGStepStatus.SKIPPED)
        
        return {
            'dag_id': self.dag_id,
            'run_id': self.run_id,
            'status': self.status.value,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'skipped_steps': skipped_steps,
            'total_retries': self.total_retries,
            'duration_seconds': self.duration_seconds,
            'success_rate': (completed_steps / total_steps * 100) if total_steps > 0 else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'dag_id': self.dag_id,
            'run_id': self.run_id,
            'status': self.status.value,
            'steps': {sid: step.to_dict() for sid, step in self.steps.items()},
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_retries': self.total_retries,
            'error': self.error,
            'metadata': self.metadata,
            'duration_seconds': self.duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DAGRun':
        """Create from dictionary."""
        run = cls(
            dag_id=data['dag_id'],
            run_id=data['run_id'],
            status=DAGRunStatus(data['status']),
            total_retries=data.get('total_retries', 0),
            error=data.get('error'),
            metadata=data.get('metadata', {})
        )
        
        # Restore timestamps
        if data.get('start_time'):
            run.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            run.end_time = datetime.fromisoformat(data['end_time'])
        
        # Restore steps
        for step_id, step_data in data.get('steps', {}).items():
            run.steps[step_id] = DAGStepState.from_dict(step_data)
        
        return run