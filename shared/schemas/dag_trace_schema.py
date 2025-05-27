"""
Schema definitions for DAGRun execution traces.

This module defines the data structures for capturing detailed
execution traces of DAG runs and their steps.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class TraceEventType(Enum):
    """Types of events that can be traced."""
    DAG_START = "dag_start"
    DAG_COMPLETE = "dag_complete"
    DAG_FAIL = "dag_fail"
    STEP_START = "step_start"
    STEP_COMPLETE = "step_complete"
    STEP_FAIL = "step_fail"
    STEP_RETRY = "step_retry"
    STEP_SKIP = "step_skip"
    ERROR = "error"
    INFO = "info"
    DEBUG = "debug"


@dataclass
class StepTraceEntry:
    """Trace entry for a single step execution."""
    step_id: str
    event_type: TraceEventType
    timestamp: datetime
    duration_ms: Optional[int] = None
    retry_attempt: int = 0
    agent_name: Optional[str] = None
    task_type: Optional[str] = None
    input_summary: Optional[Dict[str, Any]] = None
    output_summary: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'step_id': self.step_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'duration_ms': self.duration_ms,
            'retry_attempt': self.retry_attempt,
            'agent_name': self.agent_name,
            'task_type': self.task_type,
            'input_summary': self.input_summary,
            'output_summary': self.output_summary,
            'error_details': self.error_details,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepTraceEntry':
        """Create from dictionary."""
        return cls(
            step_id=data['step_id'],
            event_type=TraceEventType(data['event_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            duration_ms=data.get('duration_ms'),
            retry_attempt=data.get('retry_attempt', 0),
            agent_name=data.get('agent_name'),
            task_type=data.get('task_type'),
            input_summary=data.get('input_summary'),
            output_summary=data.get('output_summary'),
            error_details=data.get('error_details'),
            metadata=data.get('metadata', {})
        )


@dataclass
class DAGRunTrace:
    """Complete execution trace for a DAG run."""
    run_id: str
    dag_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    trace_entries: List[StepTraceEntry] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def add_entry(self, entry: StepTraceEntry) -> None:
        """Add a trace entry."""
        self.trace_entries.append(entry)
        
        # Update counters based on event type
        if entry.event_type == TraceEventType.STEP_START:
            self.total_steps += 1
        elif entry.event_type == TraceEventType.STEP_COMPLETE:
            self.completed_steps += 1
        elif entry.event_type == TraceEventType.STEP_FAIL:
            self.failed_steps += 1
        elif entry.event_type == TraceEventType.STEP_SKIP:
            self.skipped_steps += 1
    
    def get_step_trace(self, step_id: str) -> List[StepTraceEntry]:
        """Get all trace entries for a specific step."""
        return [entry for entry in self.trace_entries if entry.step_id == step_id]
    
    def get_events_by_type(self, event_type: TraceEventType) -> List[StepTraceEntry]:
        """Get all trace entries of a specific event type."""
        return [entry for entry in self.trace_entries if entry.event_type == event_type]
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate execution summary."""
        duration_ms = None
        if self.end_time and self.start_time:
            duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
        
        return {
            'run_id': self.run_id,
            'dag_id': self.dag_id,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_ms': duration_ms,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'failed_steps': self.failed_steps,
            'skipped_steps': self.skipped_steps,
            'total_events': len(self.trace_entries),
            'custom_summary': self.summary
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'run_id': self.run_id,
            'dag_id': self.dag_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'failed_steps': self.failed_steps,
            'skipped_steps': self.skipped_steps,
            'trace_entries': [entry.to_dict() for entry in self.trace_entries],
            'summary': self.summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DAGRunTrace':
        """Create from dictionary."""
        trace = cls(
            run_id=data['run_id'],
            dag_id=data['dag_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            status=data.get('status', 'running'),
            total_steps=data.get('total_steps', 0),
            completed_steps=data.get('completed_steps', 0),
            failed_steps=data.get('failed_steps', 0),
            skipped_steps=data.get('skipped_steps', 0),
            summary=data.get('summary', {})
        )
        
        # Reconstruct trace entries
        for entry_data in data.get('trace_entries', []):
            trace.trace_entries.append(StepTraceEntry.from_dict(entry_data))
        
        return trace